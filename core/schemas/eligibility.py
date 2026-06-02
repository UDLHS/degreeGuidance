"""Pydantic request/response models for the eligibility engine (Phase 6).

These are the API contract for POST /api/v1/eligibility. The engine
(core/eligibility/engine.py) consumes EligibilityRequest and produces
EligibilityResponse. Nothing here touches the DB.

Design notes:
- The request accepts human-friendly *codes* (district_code='COLOMBO',
  stream_code='BIO_SCIENCE'), not internal integer IDs. The engine resolves
  codes -> IDs and raises a 422 if a code is unknown.
- z_score bounds [-2.0, 3.0] match the validator range documented on
  z_score_cutoffs.z_score (handbook observed range ~[-0.7, 2.9]).
- exam_year is optional; when omitted the engine uses the most recent A/L year
  loaded in z_score_cutoffs. With only year=2023 loaded today, that is 2023.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class EligibilityRequest(BaseModel):
    z_score: float = Field(
        ...,
        ge=-2.0,
        le=3.0,
        description="Student's A/L Z-score. Range [-2.0, 3.0].",
    )
    district_code: str = Field(
        ...,
        min_length=1,
        description="District code, e.g. 'COLOMBO'. Resolved to districts.district_id.",
    )
    stream_code: str = Field(
        ...,
        min_length=1,
        description="Stream code, e.g. 'BIO_SCIENCE'. Resolved to streams.stream_id.",
    )
    exam_year: int | None = Field(
        default=None,
        ge=2000,
        le=2100,
        description=(
            "A/L exam year (NOT the handbook publication year). "
            "Defaults to the most recent year loaded in z_score_cutoffs."
        ),
    )

    @field_validator("district_code", "stream_code")
    @classmethod
    def _normalize_code(cls, v: str) -> str:
        # Codes are stored uppercase; normalize so 'colombo' resolves too.
        return v.strip().upper()


class EligibilityResultItem(BaseModel):
    course_code: str
    course_number: str | None
    course_name: str
    university_code: str
    university_name: str
    university_district_id: int
    duration_years: float | None
    cutoff_z_score: float
    student_margin: float = Field(
        ...,
        description="student z_score minus cutoff. >= 0 for every returned course.",
    )
    selection_basis: str
    requires_aptitude_test: bool
    status: Literal["eligible", "conditional"] = Field(
        ...,
        description="'conditional' when the course also requires an aptitude test.",
    )
    is_marginal: bool = Field(
        ...,
        description="True when student_margin <= 0.05 (cutoff could shift next year).",
    )
    available_mediums: list[str] = Field(
        default_factory=list,
        description="Medium codes (SI/TA/EN). Empty until course_mediums is populated (Phase 9).",
    )


class EligibilityResponse(BaseModel):
    exam_year_used: int
    confidence_tier: Literal["current", "previous_year", "estimated"]
    confidence_message: str | None
    student_z_score: float
    district_code: str
    stream_code: str
    eligible_count: int
    conditional_count: int
    total_count: int
    results: list[EligibilityResultItem]
