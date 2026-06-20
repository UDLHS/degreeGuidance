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


class UniversityOut(BaseModel):
    code: str
    name_en: str
    short_name: str | None = None


class ReferenceResponse(BaseModel):
    districts: list[DistrictOut]
    streams: list[StreamOut]
    universities: list[UniversityOut]
