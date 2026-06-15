"""Recommendation service (Week 3, masterplan §9).

Composes the deterministic pieces: run the eligibility engine, score + rank the
eligible courses with the active config, and add the stream-eligible programmes
that have no usable cutoff in the student's district (so none disappear). No LLM.
"""

from __future__ import annotations

from collections import Counter

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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
    scorables = [
        ScorableCourse(
            course_code=it.course_code,
            cutoff_z_score=it.cutoff_z_score,
            student_margin=it.student_margin,
            university_code=it.university_code,
            university_district_id=it.university_district_id,
        )
        for it in elig.results
    ]
    scored = score_courses(scorables, profile, config)
    item_by_code = {it.course_code: it for it in elig.results}

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
        bucket_counts=dict(Counter(s.bucket for s in scored)),
        recommendations=recommendations,
        also_offered_no_cutoff_count=also_count,
        also_offered_no_cutoff=also,
    )
