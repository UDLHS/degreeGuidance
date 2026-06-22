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

_VALID_GRADES = {"F", "S", "C", "B", "A"}


class SubjectInput(BaseModel):
    """One A/L subject + grade. Grades: F(ail)/S(ordinary pass)/C(redit)/B/A."""

    subject: str = Field(..., min_length=1, max_length=100)
    grade: str = Field(..., min_length=1, max_length=1)

    @field_validator("grade")
    @classmethod
    def _validate_grade(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in _VALID_GRADES:
            raise ValueError(f"grade must be one of {sorted(_VALID_GRADES)}, got {v!r}")
        return v


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
    subjects: list[SubjectInput] = Field(
        ...,
        min_length=3,
        max_length=3,
        description=(
            "The student's 3 A/L subjects + grades. Required: many courses gate on "
            "exact subject combinations beyond stream (e.g. Engineering requires "
            "Chemistry specifically; a Physics+Maths+ICT student doesn't qualify "
            "even though they're in the Physical Science stream). See handbook §2.2."
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
    subject_filtered_count: int = Field(
        default=0,
        description=(
            "Courses that cleared the stream + Z-score cutoff but were excluded "
            "because the student's exact subject combination doesn't satisfy the "
            "course's §2.2 prerequisite (e.g. Engineering requires Chemistry)."
        ),
    )
    results: list[EligibilityResultItem]
