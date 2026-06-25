"""Deterministic recommendation scorer — Week 3 (masterplan §9).

Pure (no DB, no LLM): given a student profile, the eligible courses, and the
active scoring config, it produces a transparent weighted score per course, a
visible per-dimension breakdown, and a Safe/Ambitious/… bucket.

Five §9 dimensions, but only the ones with data contribute; the rest are inert
and the weights renormalize over the active ones, so results stay sensible today
and the soft dimensions (interest/career/industry) switch on with no rework when
the Week 4-5 agent/RAG layer lands.

  active now : z_margin (always), university (only if the student named preferred
               universities — otherwise it's a non-signal, not a district bonus,
               which keeps "no preferences -> normal safety recommend" honest).
  inert now  : interest, career, industry  -> return None.

The LLM never touches a score (§20 principle #1) — it only writes explanations
on top, later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import tanh
from typing import Callable, Optional


@dataclass(frozen=True)
class ScoringProfile:
    z_score: float
    district_id: int
    preferred_university_codes: frozenset[str] = frozenset()
    # carried for the Week 4-5 soft dimensions; unused by the active scorer.
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
    bucket: str  # safe | ambitious | hidden | consider
    is_marginal: bool
    breakdown: list[DimensionScore] = field(default_factory=list)


# --- dimension functions: return a 0..1 score, or None if not computable/inert ---

def _z_margin(course: ScorableCourse, profile: ScoringProfile, th: dict) -> float:
    # tanh of the margin (masterplan §9.1), mapped from [-1,1] to [0,1] so
    # at-cutoff -> 0.5, comfortably above -> ~1, just-barely -> <0.5.
    scale = float(th.get("z_margin_tanh_scale", 4.0))
    return (tanh(course.student_margin * scale) + 1.0) / 2.0


def _university(course: ScorableCourse, profile: ScoringProfile, th: dict) -> Optional[float]:
    if not profile.preferred_university_codes:
        return None  # inert without a preferred list — not a hidden district bonus
    if course.university_code in profile.preferred_university_codes:
        return 1.0
    if course.university_district_id == profile.district_id:
        return 0.5
    return 0.2


def _interest(course: ScorableCourse, profile: ScoringProfile, th: dict) -> Optional[float]:
    return course.interest_score  # None when student typed no interests → inert


def _inert(course: ScorableCourse, profile: ScoringProfile, th: dict) -> Optional[float]:
    return None  # career/industry — future


DimensionFn = Callable[[ScorableCourse, ScoringProfile, dict], Optional[float]]

DIMENSIONS: list[tuple[str, DimensionFn]] = [
    ("z_margin", _z_margin),
    ("university", _university),
    ("interest", _interest),
    ("career", _inert),
    ("industry", _inert),
]


def _bucket(total: float, margin: float, th: dict) -> str:
    # §9.2 — Hidden needs industry-tag data (Week 4-5), so it can't fire yet.
    if total >= float(th["safe_score"]) and margin >= float(th["safe_margin"]):
        return "safe"
    if total >= float(th["ambitious_score"]) and margin < float(th["ambitious_margin"]):
        return "ambitious"
    return "consider"


def score_course(course: ScorableCourse, profile: ScoringProfile, config: dict) -> ScoredCourse:
    weights: dict = config["weights"]
    thresholds: dict = config["thresholds"]

    breakdown: list[DimensionScore] = []
    for name, fn in DIMENSIONS:
        raw = fn(course, profile, thresholds)
        if raw is None:
            continue
        breakdown.append(DimensionScore(name=name, weight=float(weights.get(name, 0.0)),
                                        raw_score=raw, contribution=0.0))

    active_weight = sum(d.weight for d in breakdown) or 1.0
    renorm = [
        DimensionScore(d.name, round(d.weight / active_weight, 4), round(d.raw_score, 4),
                       round((d.weight / active_weight) * d.raw_score, 4))
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
