"""Pydantic request/response models for recommendations (Week 3, masterplan §9).

POST /api/v1/recommendations. Extends the eligibility request with the student's
preferences (university shortlist + the soft signals carried for Week 4-5), and
returns the eligible courses ranked by the deterministic scorer with a visible
per-dimension breakdown, plus the programmes offered in the student's stream that
have no usable cutoff in their district (so nothing silently disappears).
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from core.schemas.eligibility import EligibilityRequest


class RecommendationRequest(EligibilityRequest):
    preferred_university_codes: list[str] = Field(default_factory=list)
    interests: str | None = Field(default=None, max_length=2000)
    career_tags: list[str] = Field(default_factory=list)
    industry_tags: list[str] = Field(default_factory=list)

    @field_validator("preferred_university_codes")
    @classmethod
    def _upper_unis(cls, v: list[str]) -> list[str]:
        return [c.strip().upper() for c in v if c.strip()]


class DimensionBreakdownItem(BaseModel):
    name: str
    weight: float  # renormalized over active dimensions
    raw_score: float
    contribution: float


class ScoredRecommendation(BaseModel):
    course_code: str
    course_name: str
    university_code: str
    university_name: str
    cutoff_z_score: float
    student_margin: float
    selection_basis: str
    requires_aptitude_test: bool
    status: str  # eligible | conditional
    is_marginal: bool
    available_mediums: list[str]
    eligible_stream_codes: list[str] = Field(
        default_factory=list,
        description="Stream codes (e.g. BIO_SCIENCE) that are eligible for this course.",
    )
    total_score: float
    bucket: str  # safe | ambitious | hidden | consider
    breakdown: list[DimensionBreakdownItem]


class AlsoOfferedItem(BaseModel):
    course_code: str
    course_name: str
    university_code: str
    university_name: str
    reason: str = "no_cutoff_in_district"


class RecommendationResponse(BaseModel):
    exam_year_used: int
    confidence_tier: str
    confidence_message: str | None
    mode: str  # "preference" | "normal"
    eligible_count: int
    conditional_count: int
    subject_filtered_count: int = 0
    bucket_counts: dict[str, int]
    recommendations: list[ScoredRecommendation]
    also_offered_no_cutoff_count: int
    also_offered_no_cutoff: list[AlsoOfferedItem]
