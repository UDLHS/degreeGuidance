"""Public reference-data schemas (Week 3, Part 1 UI).

Backs GET /api/v1/reference, which the student form uses to populate the
district/stream/university pickers from the real DB — never hardcoded in the
frontend, so the UI can never drift from the actual catalog.
"""

from __future__ import annotations

from pydantic import BaseModel


class DistrictOut(BaseModel):
    code: str
    name_en: str
    is_disadvantaged: bool


class StreamOut(BaseModel):
    code: str
    name_en: str
    description: str | None = None
    subjects: list[str] = []


class UniversityOut(BaseModel):
    code: str
    name_en: str
    short_name: str | None = None


class ReferenceResponse(BaseModel):
    districts: list[DistrictOut]
    streams: list[StreamOut]
    universities: list[UniversityOut]


# ── Exam years with promoted cutoff data (Phase 2 plan §1.1) ─────────────────

class ExamYearOut(BaseModel):
    year: int
    is_latest: bool


class YearsResponse(BaseModel):
    """Years a student can select. `years` is newest-first; exactly one entry
    has is_latest=True (the engine's default when no exam_year is sent)."""

    years: list[ExamYearOut]


class CutoffHistoryResponse(BaseModel):
    """Effective cutoff per course per year for one (district, stream) —
    STREAM-AWARE: a course with a stream-specific override (e.g. 107L) shows
    the value the requested stream actually competes against, matching the
    eligibility engine's COALESCE semantics. Year keys are strings (JSON).
    Powers the results-page trend chips/popovers (Phase 2 plan §1.4)."""

    district_code: str
    stream_code: str
    years: list[int]  # newest first
    courses: dict[str, dict[str, float]]  # course_code -> {"2024": 1.2409, ...}
