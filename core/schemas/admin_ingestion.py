"""Pydantic schemas for admin ingestion endpoints (Admin Slice 1, Part C1).

Covers the three C1 endpoints (masterplan §14.3, handoff §7):
- POST /api/admin/ingestions       -> IngestionCreateResponse (Step 4 summary)
- GET  /api/admin/ingestions       -> IngestionRunListResponse
- GET  /api/admin/ingestions/{id}  -> IngestionRunDetail (run + parse_errors)

Read models mirror the IngestionRun / ParseError ORM columns exactly (the loader
owns these tables), so from_attributes can populate them straight off the ORM rows.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class IngestionCreateResponse(BaseModel):
    """Result of a POST to /ingestions (CSV-direct, PDF-upload, or promote).

    For the synchronous CSV path and /promote, processed/failed mirror the
    ingest_zscores() return dict. For the async PDF path, status='running' and
    processed/failed are null until the Arq extraction job completes.
    """

    run_id: str
    status: str
    run_type: str
    processed: int | None = None
    failed: int | None = None


class IngestionRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: uuid.UUID
    run_type: str
    source_label: str | None = None
    year: int | None = None
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    records_processed: int | None = None
    records_failed: int | None = None
    triggered_by: str | None = None
    notes: str | None = None
    error_log: str | None = None


class IngestionRunListResponse(BaseModel):
    total: int
    items: list[IngestionRunOut]


class ParseErrorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    error_id: int
    run_id: uuid.UUID | None = None
    source_label: str | None = None
    page_number: int | None = None
    raw_block: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    resolved: bool
    resolved_action: str | None = None
    created_at: datetime


class IngestionRunDetail(IngestionRunOut):
    """A single run plus its parse_errors triage queue."""

    parse_error_count: int
    parse_errors: list[ParseErrorOut]


# ── Handbook change-set (Phase A1 diff engine) ──────────────────────────────

class HandbookChangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    change_id: int
    run_id: uuid.UUID
    change_type: str
    course_code: str
    summary: str | None = None
    before_value: dict[str, Any] | None = None
    after_value: dict[str, Any] | None = None
    status: str
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime


class HandbookChangeListResponse(BaseModel):
    total: int
    counts: dict[str, int]  # e.g. {"pending": 6, "approved": 2, ...}
    items: list[HandbookChangeOut]


class HandbookChangeUpdate(BaseModel):
    """Approve/reject one change. For a course_added the admin also supplies the
    university_id + name_en the cutoff table can't give us, so apply can create
    a valid (inactive) course stub."""

    status: Literal["approved", "rejected"]
    notes: str | None = None
    university_id: int | None = Field(default=None, description="required to apply a course_added")
    name_en: str | None = Field(default=None, description="required to apply a course_added")


class ChangeApplyResponse(BaseModel):
    applied_removed: int
    applied_added: int
    skipped: list[dict[str, Any]]
