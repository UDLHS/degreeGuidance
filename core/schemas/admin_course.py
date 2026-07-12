"""Pydantic schemas for admin course endpoints (Admin Slice 1, Part B2).

Editable fields follow masterplan §14.1 ("add a course, edit a name, flip
is_active, change selection_basis or requires_aptitude_test") plus the obvious
descriptive columns. Structural keys — course_code (PK), university_id,
faculty_id, metadata, timestamps — are intentionally NOT patchable here;
university/faculty management is a separate admin surface.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SelectionBasis = Literal["district_quota", "all_island_merit"]


class CourseCreate(BaseModel):
    course_code: str = Field(..., min_length=1, max_length=15)
    university_id: int = Field(..., ge=1)
    name_en: str = Field(..., min_length=1, max_length=300)
    selection_basis: SelectionBasis = "district_quota"
    requires_aptitude_test: bool = False
    course_number: str | None = Field(default=None, max_length=5)
    faculty_id: int | None = Field(default=None, ge=1)
    name_si: str | None = Field(default=None, max_length=400)
    name_ta: str | None = Field(default=None, max_length=400)
    degree_type: str | None = Field(default=None, max_length=50)
    duration_years: float | None = Field(default=None, ge=0, le=10)
    description: str | None = None
    career_outlook: str | None = None
    is_active: bool = True
    first_intake_year: int | None = Field(default=None, ge=1900, le=2100)

    @field_validator("course_code")
    @classmethod
    def _upper(cls, v: str) -> str:
        return v.strip().upper()


class CourseUpdate(BaseModel):
    # all optional; only the §14.1 allowlist is editable
    name_en: str | None = Field(default=None, min_length=1, max_length=300)
    name_si: str | None = Field(default=None, max_length=400)
    name_ta: str | None = Field(default=None, max_length=400)
    degree_type: str | None = Field(default=None, max_length=50)
    duration_years: float | None = Field(default=None, ge=0, le=10)
    selection_basis: SelectionBasis | None = None
    requires_aptitude_test: bool | None = None
    description: str | None = None
    career_outlook: str | None = None
    is_active: bool | None = None
    first_intake_year: int | None = Field(default=None, ge=1900, le=2100)


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    course_code: str
    course_number: str | None = None
    university_id: int
    faculty_id: int | None = None
    name_en: str
    name_si: str | None = None
    name_ta: str | None = None
    degree_type: str | None = None
    duration_years: float | None = None
    selection_basis: str
    requires_aptitude_test: bool
    description: str | None = None
    career_outlook: str | None = None
    is_active: bool
    first_intake_year: int | None = None
    created_at: datetime
    updated_at: datetime
    # joined from universities (read-only context)
    university_code: str | None = None
    university_name_en: str | None = None
    # Phase 8.4 safety signal — set when a mutation leaves the course active
    # with ZERO eligible streams (the engine's EXISTS gate then hides it from
    # every student, silently). Never persisted; response-only.
    warning: str | None = None


class CourseStreamsUpdate(BaseModel):
    """Replace-set of eligible stream codes for one course (Phase 8.1)."""

    stream_codes: list[str] = Field(
        default_factory=list,
        description="Full new set, e.g. ['PHYSICAL_SCIENCE','ENGINEERING_TECH']. Empty = none.",
    )

    @field_validator("stream_codes")
    @classmethod
    def _norm(cls, v: list[str]) -> list[str]:
        seen: list[str] = []
        for c in v:
            c = c.strip().upper()
            if c and c not in seen:
                seen.append(c)
        return seen


class CourseStreamsOut(BaseModel):
    course_code: str
    is_active: bool
    stream_codes: list[str]
    warning: str | None = None


class CourseListResponse(BaseModel):
    total: int
    items: list[CourseOut]
