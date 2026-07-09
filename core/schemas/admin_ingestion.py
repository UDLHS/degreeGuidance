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
    cutoff_pages: str | None = None


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


# ── Staged extraction lifecycle (Phase 1 pipeline) ──────────────────────────

class ExtractPagesRequest(BaseModel):
    """Manual page-range re-extraction, e.g. '179-188' or '150-156,179-188'."""

    cutoff_pages: str = Field(..., min_length=1, max_length=100)


class ExtractionColumnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    column_id: int
    column_key: str
    page_number: int
    raw_label: str
    markers: str | None = None
    suggested_course_code: str | None = None
    suggestion_confidence: float | None = None
    mapped_course_code: str | None = None
    status: str
    override_streams: str | None = None
    suggested_override_streams: list[str] = Field(default_factory=list)
    has_data: bool | None = None  # column carries >=1 real z-score (None = unknown)


class ColumnListResponse(BaseModel):
    run_status: str
    cutoff_pages: str | None = None
    total: int
    counts: dict[str, int]                 # by column status
    duplicate_mappings: dict[str, int]     # mapped/suggested code -> #columns
    items: list[ExtractionColumnOut]


class ColumnUpdate(BaseModel):
    """Confirm/correct one column. Setting mapped_course_code confirms it;
    status='ignored' excludes the column; status='pending' reopens it;
    status='unmapped_kept' preserves the column's z-scores WITHOUT a Uni-Code
    (for a column that has data but no code in the book's Uni-Code section).
    override_streams marks this column as a deliberate stream-variant of a
    code another confirmed column in the run also targets (comma-separated
    stream codes, e.g. 'COMMERCE' or 'BIO_SCIENCE,PHYSICAL_SCIENCE'); pass ''
    to clear it back to the normal 1:1 case."""

    mapped_course_code: str | None = Field(default=None, max_length=15)
    status: Literal["confirmed", "ignored", "pending", "unmapped_kept"] | None = None
    override_streams: str | None = Field(default=None, max_length=200)


class BulkConfirmResponse(BaseModel):
    confirmed: int
    remaining_pending: int


class MappingConfirmResponse(BaseModel):
    columns_used: int
    columns_ignored: int
    csv_ready: bool
    changes: dict[str, int]                # change_type -> count
    aliases_learned: int
    stream_variant_columns: int = 0        # confirmed columns written as stream overrides
    unmapped_kept_columns: int = 0         # columns preserved without a Uni-Code
