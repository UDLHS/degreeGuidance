"""Recommendation service (Week 3, masterplan §9).

Composes the deterministic pieces: run the eligibility engine, score + rank the
eligible courses with the active config, and add the stream-eligible programmes
that have no usable cutoff in the student's district (so none disappear). No LLM.
"""

from __future__ import annotations

import re
from collections import Counter

from google import genai
from google.genai.types import EmbedContentConfig
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.eligibility.engine import (
    _resolve_district_id,
    _resolve_stream_id,
    evaluate_eligibility,
)
from core.schemas.eligibility import EligibilityRequest
from core.schemas.recommendation import (
    AlsoOfferedItem,
    DimensionBreakdownItem,
    RecommendationRequest,
    RecommendationResponse,
    ScoredRecommendation,
)
from core.scoring.config import load_active_config
from core.scoring.engine import ScorableCourse, ScoringProfile, score_courses

_gemini_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=settings.gemini_api_key)
    return _gemini_client


def _course_number(course_code: str) -> str:
    """'119D' → '119'  (strip trailing alpha suffix)."""
    return re.sub(r"[A-Za-z]+$", "", course_code)


async def _interest_scores(
    session: AsyncSession,
    interest_text: str,
    course_codes: list[str],
) -> dict[str, float]:
    """Embed interest_text and return {course_code: max_cosine_similarity} for each code."""
    if not interest_text.strip() or not course_codes:
        return {}

    # Embed the student's interest text as a query vector
    client = _get_client()
    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=interest_text.strip(),
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=settings.gemini_embedding_dim,
        ),
    )
    vec = result.embeddings[0].values

    # Map each course_code to its course_number for the chunks lookup
    numbers = list({_course_number(c) for c in course_codes})

    # One pgvector query: best-matching chunk similarity per course_number
    rows = (
        await session.execute(
            text(
                "SELECT ds.course_number, "
                "MAX(1 - (c.embedding <=> CAST(:vec AS vector))) AS score "
                "FROM chunks c "
                "JOIN document_sources ds ON ds.source_id = c.source_id "
                "WHERE ds.course_number = ANY(:numbers) "
                "GROUP BY ds.course_number"
            ),
            {"vec": f"[{','.join(str(v) for v in vec)}]", "numbers": numbers},
        )
    ).all()

    # Build number → score lookup, then map back to course_codes
    number_score: dict[str, float] = {r.course_number: float(r.score) for r in rows}
    return {
        code: number_score[_course_number(code)]
        for code in course_codes
        if _course_number(code) in number_score
    }


# stream-eligible, active courses with NO usable cutoff for (year, district)
_ALSO_OFFERED_FROM = (
    "FROM courses c JOIN universities u ON u.university_id = c.university_id "
    "WHERE c.is_active = TRUE "
    "AND EXISTS (SELECT 1 FROM course_stream_eligibility cse "
    "            WHERE cse.course_code = c.course_code AND cse.stream_id = :sid) "
    "AND NOT EXISTS (SELECT 1 FROM z_score_cutoffs zc "
    "                WHERE zc.course_code = c.course_code AND zc.year = :yr "
    "                AND zc.district_id = :did AND zc.z_score IS NOT NULL)"
)


async def _also_offered(session, stream_id, district_id, year, limit=50):
    params = {"sid": stream_id, "did": district_id, "yr": year}
    count = (
        await session.execute(text(f"SELECT count(*) {_ALSO_OFFERED_FROM}"), params)
    ).scalar_one()
    rows = (
        await session.execute(
            text(
                "SELECT c.course_code, c.name_en AS course_name, u.code AS university_code, "
                f"u.name_en AS university_name {_ALSO_OFFERED_FROM} "
                "ORDER BY c.course_code LIMIT :limit"
            ),
            {**params, "limit": limit},
        )
    ).mappings().all()
    items = [
        AlsoOfferedItem(
            course_code=r["course_code"],
            course_name=r["course_name"],
            university_code=r["university_code"],
            university_name=r["university_name"],
        )
        for r in rows
    ]
    return count, items


async def recommend(session: AsyncSession, req: RecommendationRequest) -> RecommendationResponse:
    elig = await evaluate_eligibility(
        session,
        EligibilityRequest(
            z_score=req.z_score,
            district_code=req.district_code,
            stream_code=req.stream_code,
            exam_year=req.exam_year,
            subjects=req.subjects,
        ),
    )
    config = await load_active_config(session)
    district_id = await _resolve_district_id(session, req.district_code.strip().upper())
    stream_id = await _resolve_stream_id(session, req.stream_code.strip().upper())

    profile = ScoringProfile(
        z_score=req.z_score,
        district_id=district_id,
        preferred_university_codes=frozenset(req.preferred_university_codes),
        interests=req.interests,
        career_tags=frozenset(req.career_tags),
        industry_tags=frozenset(req.industry_tags),
    )

    # Pre-compute interest scores via pgvector when student typed interests
    interest_map: dict[str, float] = {}
    if req.interests and req.interests.strip():
        interest_map = await _interest_scores(
            session,
            req.interests,
            [it.course_code for it in elig.results],
        )

    scorables = [
        ScorableCourse(
            course_code=it.course_code,
            cutoff_z_score=it.cutoff_z_score,
            student_margin=it.student_margin,
            university_code=it.university_code,
            university_district_id=it.university_district_id,
            interest_score=interest_map.get(it.course_code),
        )
        for it in elig.results
    ]
    scored = score_courses(scorables, profile, config)
    item_by_code = {it.course_code: it for it in elig.results}

    # Bulk-fetch eligible stream codes for every result in one query.
    result_codes = [it.course_code for it in elig.results]
    stream_rows = (
        await session.execute(
            text(
                "SELECT cse.course_code, s.code AS stream_code "
                "FROM course_stream_eligibility cse "
                "JOIN streams s ON s.stream_id = cse.stream_id "
                "WHERE cse.course_code = ANY(:codes)"
            ),
            {"codes": result_codes},
        )
    ).all()
    streams_by_code: dict[str, list[str]] = {}
    for row in stream_rows:
        streams_by_code.setdefault(row.course_code, []).append(row.stream_code)

    recommendations = [
        ScoredRecommendation(
            course_code=it.course_code,
            course_name=it.course_name,
            university_code=it.university_code,
            university_name=it.university_name,
            cutoff_z_score=it.cutoff_z_score,
            student_margin=it.student_margin,
            selection_basis=it.selection_basis,
            requires_aptitude_test=it.requires_aptitude_test,
            status=it.status,
            is_marginal=it.is_marginal,
            available_mediums=it.available_mediums,
            eligible_stream_codes=sorted(streams_by_code.get(it.course_code, [])),
            total_score=s.total_score,
            bucket=s.bucket,
            breakdown=[
                DimensionBreakdownItem(
                    name=d.name, weight=d.weight, raw_score=d.raw_score, contribution=d.contribution
                )
                for d in s.breakdown
            ],
        )
        for s in scored
        for it in [item_by_code[s.course_code]]
    ]

    also_count, also = await _also_offered(session, stream_id, district_id, elig.exam_year_used)

    return RecommendationResponse(
        exam_year_used=elig.exam_year_used,
        confidence_tier=elig.confidence_tier,
        confidence_message=elig.confidence_message,
        mode="preference" if profile.has_preferences else "normal",
        eligible_count=elig.eligible_count,
        conditional_count=elig.conditional_count,
        subject_filtered_count=elig.subject_filtered_count,
        bucket_counts=dict(Counter(s.bucket for s in scored)),
        recommendations=recommendations,
        also_offered_no_cutoff_count=also_count,
        also_offered_no_cutoff=also,
    )
