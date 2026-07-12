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

# ---------------------------------------------------------------------------
# Career / industry tag extraction from free-form interest text
# ---------------------------------------------------------------------------

# Maps keywords found in student interest text → canonical career tags.
# Substring match (case-insensitive) against the student's interest field.
_CAREER_KEYWORDS: list[tuple[list[str], list[str]]] = [
    # IT / Software
    (["software engineer", "programmer", "coding", "code", "software dev"],
     ["software engineer"]),
    (["web developer", "web dev", "frontend", "backend", "full stack"],
     ["web developer"]),
    (["mobile app", "android", "ios developer"],
     ["mobile app developer"]),
    (["data scientist", "data science", "machine learning", "ml engineer", "ai engineer",
      "artificial intelligence"],
     ["data scientist", "ai engineer"]),
    (["data analyst", "data analysis", "business intelligence"],
     ["data analyst"]),
    (["cybersecurity", "cyber security", "security engineer", "ethical hacker"],
     ["cybersecurity analyst"]),
    (["devops", "cloud engineer", "cloud architect"],
     ["devops engineer", "cloud engineer"]),
    (["network engineer", "network admin", "network administrator"],
     ["network engineer"]),
    (["software tester", "qa engineer", "quality assurance engineer"],
     ["qa engineer"]),
    (["ui/ux", "ux designer", "user experience"],
     ["ui/ux designer"]),
    # Engineering
    (["civil engineer", "structural engineer", "construction engineer"],
     ["civil engineer"]),
    (["mechanical engineer", "machine design"],
     ["mechanical engineer"]),
    (["electrical engineer", "electronics engineer"],
     ["electrical engineer"]),
    (["chemical engineer", "process engineer"],
     ["chemical engineer"]),
    (["marine engineer", "naval architect", "shipbuilding"],
     ["marine engineer"]),
    (["engineering", "engineer"],
     ["engineer"]),
    # Healthcare
    (["doctor", "physician", "mbbs", "medical officer", "medicine"],
     ["medical officer", "doctor"]),
    (["surgeon", "surgery"],
     ["surgeon"]),
    (["dentist", "dental", "orthodontist"],
     ["dental surgeon"]),
    (["nurse", "nursing"],
     ["nurse", "nursing officer"]),
    (["pharmacist", "pharmacy"],
     ["pharmacist"]),
    (["physiotherapist", "physiotherapy"],
     ["physiotherapist"]),
    (["occupational therapist", "occupational therapy"],
     ["occupational therapist"]),
    (["speech therapist", "audiologist", "speech and hearing"],
     ["speech therapist"]),
    (["optometrist", "optometry"],
     ["optometrist"]),
    (["radiographer", "radiology", "imaging technologist"],
     ["radiographer"]),
    (["medical laboratory", "lab scientist", "lab technologist"],
     ["medical laboratory scientist"]),
    (["public health", "health promotion", "epidemiologist"],
     ["public health officer"]),
    (["ayurveda", "ayurvedic"],
     ["ayurveda medical officer"]),
    # Business / Management
    (["accountant", "accounting", "auditor", "auditing"],
     ["accountant", "auditor"]),
    (["financial analyst", "finance analyst", "investment analyst"],
     ["financial analyst"]),
    (["marketing executive", "marketing manager", "brand manager", "digital marketing"],
     ["marketing executive", "brand manager"]),
    (["human resource", "hr manager", "hr executive", "talent acquisition"],
     ["human resource officer"]),
    (["entrepreneur", "business owner", "startup", "self-employed"],
     ["entrepreneur"]),
    (["manager", "management trainee", "business analyst", "operations manager"],
     ["management trainee"]),
    # Law
    (["lawyer", "attorney", "barrister", "solicitor", "legal"],
     ["attorney-at-law"]),
    (["judge", "judiciary"],
     ["judge"]),
    # Education
    (["teacher", "school teacher", "tutor", "educator"],
     ["teacher"]),
    (["lecturer", "professor", "academic"],
     ["lecturer"]),
    # Agriculture
    (["agricultural officer", "agronomist", "agronomy", "plantation manager"],
     ["agriculture officer", "agronomist"]),
    (["food technologist", "food scientist", "food technology"],
     ["food technologist"]),
    # Research
    (["researcher", "research officer", "scientist", "research scientist"],
     ["research officer"]),
    # Architecture / Design
    (["architect", "architecture"],
     ["architect"]),
    (["quantity surveyor", "qs"],
     ["quantity surveyor"]),
    (["designer", "graphic designer", "industrial designer"],
     ["designer"]),
    (["fashion designer", "textile"],
     ["fashion designer"]),
    # Journalism / Media
    (["journalist", "reporter", "news anchor", "media"],
     ["journalist"]),
    (["content writer", "editor", "copywriter"],
     ["content writer"]),
    # Social / NGO
    (["social worker", "community development", "ngo"],
     ["social worker"]),
    # Tourism / Hospitality
    (["hotel manager", "hotel", "resort manager"],
     ["hotel manager"]),
    (["travel", "tourism officer", "tour guide"],
     ["tourism officer"]),
    # Sports
    (["sports", "coach", "fitness trainer", "personal trainer"],
     ["sports coach"]),
    # Logistics
    (["supply chain", "logistics", "operations"],
     ["supply chain manager"]),
]

# Maps keywords → canonical industry tags.
_INDUSTRY_KEYWORDS: list[tuple[list[str], list[str]]] = [
    (["software", "it sector", "information technology", "tech", "coding", "programming",
      "developer", "computer science", "data", "cybersecurity", "cloud", "devops",
      "artificial intelligence", "machine learning", "ai", "startup"],
     ["it"]),
    (["healthcare", "hospital", "medical", "clinic", "health", "doctor", "nurse",
      "medicine", "pharmacy", "pharmaceutical", "dental"],
     ["healthcare"]),
    (["engineering", "construction", "civil", "structural", "mechanical",
      "electrical", "electronics", "manufacturing"],
     ["engineering"]),
    (["bank", "banking", "finance", "investment", "stock market", "financial",
      "fintech", "insurance", "accounting", "audit", "tax"],
     ["banking", "finance"]),
    (["law", "legal", "court", "attorney", "judiciary"],
     ["law"]),
    (["teach", "school", "university", "education", "training", "lecturer"],
     ["education"]),
    (["research", "r&d", "laboratory", "scientist"],
     ["research"]),
    (["agriculture", "farming", "plantation", "agronomist", "agribusiness", "food security"],
     ["agriculture"]),
    (["food", "fmcg", "food processing", "food industry"],
     ["food"]),
    (["tourism", "hotel", "hospitality", "travel", "resort", "leisure"],
     ["tourism", "hospitality"]),
    (["telecom", "telecommunications", "mobile network", "broadband"],
     ["telecommunications"]),
    (["media", "tv", "radio", "newspaper", "broadcasting", "journalism"],
     ["media"]),
    (["marketing", "advertising", "brand", "pr", "public relations", "digital marketing"],
     ["advertising", "digital marketing"]),
    (["ngo", "non-governmental", "un ", "unicef", "undp", "international development",
      "community", "social work"],
     ["ngo"]),
    (["government", "public sector", "civil service", "ministry", "state"],
     ["government"]),
    (["energy", "electricity", "power", "renewable", "solar", "wind"],
     ["energy"]),
    (["environment", "conservation", "sustainability", "green", "eco"],
     ["environment"]),
    (["logistics", "supply chain", "shipping", "port", "aviation", "freight"],
     ["logistics"]),
    (["arts", "performing arts", "theatre", "dance", "music", "film", "cinema", "visual arts"],
     ["arts"]),
    (["sports", "fitness", "gym", "athletic"],
     ["sports"]),
    (["defence", "military", "army", "navy", "air force"],
     ["defence"]),
    (["fisheries", "aquaculture", "marine", "fishery", "ocean"],
     ["fisheries", "marine"]),
]


def _kw_matches(keyword: str, text: str) -> bool:
    """True if keyword appears in text.

    Short keywords (≤4 chars, e.g. "ai", "it", "eco", "qs") are matched on
    whole-word boundaries to avoid false positives like "ai" matching "painting"
    or "eco" matching "become". Longer phrases use plain substring search.
    """
    if len(keyword) <= 4:
        return bool(re.search(r"\b" + re.escape(keyword) + r"\b", text))
    return keyword in text


def _extract_tags_from_text(text_input: str) -> tuple[list[str], list[str]]:
    """Extract career_tags and industry_tags from student's free-text interest field.

    Uses keyword matching (word-boundary-safe for short keywords) — no LLM,
    deterministic, fast.
    Returns (career_tags, industry_tags) as lowercase lists without duplicates.
    """
    lower = text_input.lower()
    career: set[str] = set()
    industry: set[str] = set()

    for keywords, tags in _CAREER_KEYWORDS:
        if any(_kw_matches(kw, lower) for kw in keywords):
            career.update(tags)

    for keywords, tags in _INDUSTRY_KEYWORDS:
        if any(_kw_matches(kw, lower) for kw in keywords):
            industry.update(tags)

    return sorted(career), sorted(industry)

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

    # W1 daily budget: interest-matching is the only Gemini dependency in the
    # recommendation path. Out of budget -> skip it gracefully (the dimension
    # goes inert; rankings still work) instead of failing the request.
    from apps.api.guards import gemini_budget

    if not gemini_budget.try_spend(1):
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


# stream-eligible, active courses with NO usable cutoff for (year, district).
# Checked for THIS student's stream specifically -- a course with no general
# cutoff but a stream-specific override for :sid (e.g. 107L, see
# course_stream_cutoff_overrides) still counts as "usable", it just isn't
# reachable through the general z_score_cutoffs row.
_ALSO_OFFERED_FROM = (
    "FROM courses c JOIN universities u ON u.university_id = c.university_id "
    "WHERE c.is_active = TRUE "
    "AND EXISTS (SELECT 1 FROM course_stream_eligibility cse "
    "            WHERE cse.course_code = c.course_code AND cse.stream_id = :sid) "
    "AND NOT EXISTS (SELECT 1 FROM z_score_cutoffs zc "
    "                WHERE zc.course_code = c.course_code AND zc.year = :yr "
    "                AND zc.district_id = :did AND zc.z_score IS NOT NULL) "
    "AND NOT EXISTS (SELECT 1 FROM course_stream_cutoff_overrides so "
    "                WHERE so.course_code = c.course_code AND so.year = :yr "
    "                AND so.district_id = :did AND so.stream_id = :sid "
    "                AND so.z_score IS NOT NULL)"
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

    # Extract career/industry tags from the student's interest text if they
    # didn't explicitly send structured tags (which the UI doesn't yet do).
    career_tags = list(req.career_tags)
    industry_tags = list(req.industry_tags)
    if req.interests and req.interests.strip() and not career_tags and not industry_tags:
        career_tags, industry_tags = _extract_tags_from_text(req.interests)

    profile = ScoringProfile(
        z_score=req.z_score,
        district_id=district_id,
        preferred_university_codes=frozenset(req.preferred_university_codes),
        interests=req.interests,
        career_tags=frozenset(career_tags),
        industry_tags=frozenset(industry_tags),
    )

    result_codes = [it.course_code for it in elig.results]

    # Pre-compute interest scores via pgvector when student typed interests
    interest_map: dict[str, float] = {}
    if req.interests and req.interests.strip():
        interest_map = await _interest_scores(
            session,
            req.interests,
            result_codes,
        )

    # Bulk-fetch career_tags and industry_tags for all eligible courses in one query.
    course_tag_rows = (
        await session.execute(
            text(
                "SELECT course_code, career_tags, industry_tags "
                "FROM courses WHERE course_code = ANY(:codes)"
            ),
            {"codes": result_codes},
        )
    ).all()
    course_career_map: dict[str, frozenset[str]] = {}
    course_industry_map: dict[str, frozenset[str]] = {}
    for row in course_tag_rows:
        course_career_map[row.course_code] = frozenset(row.career_tags or [])
        course_industry_map[row.course_code] = frozenset(row.industry_tags or [])

    scorables = [
        ScorableCourse(
            course_code=it.course_code,
            cutoff_z_score=it.cutoff_z_score,
            student_margin=it.student_margin,
            university_code=it.university_code,
            university_district_id=it.university_district_id,
            interest_score=interest_map.get(it.course_code),
            career_tags=course_career_map.get(it.course_code, frozenset()),
            industry_tags=course_industry_map.get(it.course_code, frozenset()),
        )
        for it in elig.results
    ]
    scored = score_courses(scorables, profile, config)
    item_by_code = {it.course_code: it for it in elig.results}

    # Bulk-fetch eligible stream codes for every result in one query.
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
        # near-miss window passthrough — unscored by design (not eligibility)
        later_round_margin=elig.later_round_margin,
        later_round_count=elig.later_round_count,
        later_round=elig.later_round,
        also_offered_no_cutoff_count=also_count,
        also_offered_no_cutoff=also,
    )
