"""Deterministic recommendation scorer — Week 3 (masterplan §9).

Pure (no DB, no LLM): given a student profile, the eligible courses, and the
active scoring config, it produces a transparent weighted score per course, a
visible per-dimension breakdown, and a Safe/Ambitious/… bucket.

Five §9 dimensions — all now active when data is present:

  z_margin   : always active — how far above the cutoff the student is.
  university : active only when the student named preferred universities;
               inert otherwise (prevents false district-proximity boost).
  interest   : active when the student typed interest text — cosine similarity
               vs course factsheets, rescaled so scores < 0.45 collapse to 0.
  career     : active when both the student and the course have career tags.
               0 overlap → 0.0 (not inert, not 0.5 — a clear mismatch signal).
  industry   : always active when the course has industry tags.
               • Student specified industry → match score.
               • No student preference → pure Sri-Lanka industry demand score
                 (rewards courses in structurally high-growth sectors).

The LLM never touches a score (§20 principle #1) — it only writes explanations
on top, later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import tanh
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Industry demand scores — Sri Lanka LFS 2023 + World Bank data.
# Key: lowercase industry tag exactly as stored in courses.industry_tags.
# ---------------------------------------------------------------------------

INDUSTRY_DEMAND: dict[str, float] = {
    # High-growth tech and digital
    "it": 0.95,
    "software": 0.95,
    "data": 0.90,
    "cybersecurity": 0.92,
    "ai": 0.93,
    "fintech": 0.88,
    "health tech": 0.85,
    # Healthcare
    "healthcare": 0.90,
    "medical": 0.88,
    "health": 0.87,
    "pharmaceuticals": 0.82,
    "pharma": 0.82,
    "dental care": 0.75,
    "traditional medicine": 0.55,
    # Engineering
    "engineering": 0.82,
    "electronics": 0.80,
    "manufacturing": 0.70,
    "automation": 0.78,
    "renewable energy": 0.80,
    "energy": 0.72,
    "construction": 0.72,
    "marine": 0.60,
    # Finance and business
    "banking": 0.78,
    "finance": 0.78,
    "accounting": 0.72,
    "audit": 0.70,
    "insurance": 0.72,
    "investment": 0.75,
    "real estate": 0.62,
    # Law and public sector
    "law": 0.70,
    "legal": 0.70,
    "government": 0.62,
    "public sector": 0.62,
    "public health": 0.68,
    # Connectivity and logistics
    "telecommunications": 0.75,
    "telecom": 0.75,
    "logistics": 0.68,
    "supply chain": 0.68,
    "transport": 0.65,
    # Food and retail
    "food": 0.62,
    "retail": 0.60,
    "fmcg": 0.62,
    "hospitality": 0.65,
    "tourism": 0.65,
    # Primary sectors
    "agriculture": 0.55,
    "agribusiness": 0.58,
    "plantation": 0.50,
    "fisheries": 0.52,
    "aquaculture": 0.52,
    "environment": 0.55,
    "sustainability": 0.58,
    # Education and research
    "education": 0.62,
    "research": 0.60,
    # Creative and social
    "media": 0.50,
    "advertising": 0.52,
    "digital marketing": 0.62,
    "arts": 0.40,
    "entertainment": 0.42,
    "performing arts": 0.38,
    "sports": 0.48,
    "social services": 0.48,
    "ngo": 0.45,
    "defence": 0.55,
}

_DEMAND_DEFAULT = 0.45  # fallback for unknown tags


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ScoringProfile:
    z_score: float
    district_id: int
    preferred_university_codes: frozenset[str] = frozenset()
    interests: Optional[str] = None
    career_tags: frozenset[str] = frozenset()
    industry_tags: frozenset[str] = frozenset()

    @property
    def has_preferences(self) -> bool:
        return bool(
            self.preferred_university_codes
            or (self.interests and self.interests.strip())
            or self.career_tags
            or self.industry_tags
        )


@dataclass(frozen=True)
class ScorableCourse:
    course_code: str
    cutoff_z_score: float
    student_margin: float  # student_z - cutoff (precomputed by the eligibility engine)
    university_code: str
    university_district_id: int
    interest_score: Optional[float] = None  # pre-computed cosine similarity; None → inert
    career_tags: frozenset[str] = frozenset()
    industry_tags: frozenset[str] = frozenset()


@dataclass(frozen=True)
class DimensionScore:
    name: str
    weight: float  # renormalized over active dimensions
    raw_score: float  # 0..1
    contribution: float  # weight * raw_score


@dataclass(frozen=True)
class ScoredCourse:
    course_code: str
    total_score: float
    bucket: str  # safe | ambitious | consider
    is_marginal: bool
    breakdown: list[DimensionScore] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Dimension functions: return 0..1, or None if not computable / inert
# ---------------------------------------------------------------------------

def _z_margin(course: ScorableCourse, profile: ScoringProfile, th: dict) -> float:
    scale = float(th.get("z_margin_tanh_scale", 4.0))
    return (tanh(course.student_margin * scale) + 1.0) / 2.0


def _university(course: ScorableCourse, profile: ScoringProfile, th: dict) -> Optional[float]:
    if not profile.preferred_university_codes:
        return None  # inert without a preferred list — no hidden district bonus
    if course.university_code in profile.preferred_university_codes:
        return 1.0
    if course.university_district_id == profile.district_id:
        return 0.5
    return 0.2


def _interest(course: ScorableCourse, profile: ScoringProfile, th: dict) -> Optional[float]:
    """Cosine similarity from pgvector, rescaled so scores below 0.45 → 0.

    Raw cosine similarity in the Gemini embedding space rarely falls below 0.3
    even for completely unrelated content, which would make every course look
    'somewhat relevant'. The rescaling collapses that noise floor so that a
    course with nothing to do with the student's interests scores 0, not ~0.5.
    """
    if course.interest_score is None:
        return None  # student typed no interests — inert
    MIN_SIM = 0.45
    raw = course.interest_score
    if raw <= MIN_SIM:
        return 0.0
    return min(1.0, (raw - MIN_SIM) / (1.0 - MIN_SIM))


def _career(course: ScorableCourse, profile: ScoringProfile, th: dict) -> Optional[float]:
    """Tag overlap between student career goals and course's career paths.

    Returns None when student didn't specify career goals (inert → weights
    renormalize). When career goals are specified:
      - 0 overlap  → 0.0  (not None — this actively penalises mismatches)
      - some match → proportion of the student's goals this course addresses

    Matching uses substring containment so that "engineer" matches
    "software engineer", "civil engineer", etc.
    """
    if not profile.career_tags or not course.career_tags:
        return None  # student didn't specify career goals → inert
    s_tags = {t.lower().strip() for t in profile.career_tags}
    c_tags = {t.lower().strip() for t in course.career_tags}
    matches = sum(
        1 for st in s_tags
        if any(st in ct or ct in st for ct in c_tags)
    )
    if matches == 0:
        return 0.0  # course is clearly irrelevant to this career goal
    return min(1.0, matches / len(s_tags))


def _industry(course: ScorableCourse, profile: ScoringProfile, th: dict) -> Optional[float]:
    """Industry demand score blended with student's sector preference.

    Always active when a course has industry tags. Two modes:
    • Student has industry_tags → Jaccard-style match; 0 overlap → 0.0.
    • No student preference  → pure demand score from INDUSTRY_DEMAND table.

    This rewards high-demand sectors even when the student didn't explicitly
    state an industry preference, which surfaces IT/healthcare courses
    appropriately without punishing students who leave the field blank.
    """
    if not course.industry_tags:
        return None  # no industry data for this course
    c_tags = {t.lower().strip() for t in course.industry_tags}
    demand = max(
        (INDUSTRY_DEMAND.get(t, _DEMAND_DEFAULT) for t in c_tags),
        default=_DEMAND_DEFAULT,
    )
    if not profile.industry_tags:
        # No preference stated — use market demand as a neutral quality signal.
        return demand
    s_tags = {t.lower().strip() for t in profile.industry_tags}
    matches = sum(
        1 for st in s_tags
        if any(st in ct or ct in st for ct in c_tags)
    )
    if matches == 0:
        return 0.0  # student wants X industry, course is in a different sector
    match_score = min(1.0, matches / len(s_tags))
    # 70% preference alignment + 30% market demand
    return 0.7 * match_score + 0.3 * demand


DimensionFn = Callable[[ScorableCourse, ScoringProfile, dict], Optional[float]]

DIMENSIONS: list[tuple[str, DimensionFn]] = [
    ("z_margin", _z_margin),
    ("university", _university),
    ("interest", _interest),
    ("career", _career),
    ("industry", _industry),
]


def _bucket(total: float, margin: float, th: dict) -> str:
    """Eligible courses split into safe/consider only (user decision
    2026-07-13): 'Ambitious' is now the student-facing tab for courses ABOVE
    the student's z (the later-rounds window) — never an eligible bucket.
    Tight clears live in 'consider'. th's ambitious_* keys are retained in
    stored configs but intentionally unused."""
    if total >= float(th["safe_score"]) and margin >= float(th["safe_margin"]):
        return "safe"
    return "consider"


def score_course(course: ScorableCourse, profile: ScoringProfile, config: dict) -> ScoredCourse:
    weights: dict = config["weights"]
    thresholds: dict = config["thresholds"]

    breakdown: list[DimensionScore] = []
    for name, fn in DIMENSIONS:
        raw = fn(course, profile, thresholds)
        if raw is None:
            continue
        breakdown.append(
            DimensionScore(
                name=name,
                weight=float(weights.get(name, 0.0)),
                raw_score=raw,
                contribution=0.0,
            )
        )

    active_weight = sum(d.weight for d in breakdown) or 1.0
    renorm = [
        DimensionScore(
            d.name,
            round(d.weight / active_weight, 4),
            round(d.raw_score, 4),
            round((d.weight / active_weight) * d.raw_score, 4),
        )
        for d in breakdown
    ]
    total = round(sum(d.contribution for d in renorm), 4)
    return ScoredCourse(
        course_code=course.course_code,
        total_score=total,
        bucket=_bucket(total, course.student_margin, thresholds),
        is_marginal=course.student_margin <= float(thresholds.get("marginal_band", 0.05)),
        breakdown=renorm,
    )


def score_courses(
    courses: list[ScorableCourse], profile: ScoringProfile, config: dict
) -> list[ScoredCourse]:
    """Score and rank eligible courses (highest total first; stable by code)."""
    scored = [score_course(c, profile, config) for c in courses]
    scored.sort(key=lambda s: (-s.total_score, s.course_code))
    return scored
