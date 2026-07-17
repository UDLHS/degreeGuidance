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
    # Post-promote review card (Phase 7.4) — only set by /promote:
    # promoted_year, students_now_see, coverage gaps, override/codeless counts,
    # archived file paths. None on every other path.
    checklist: dict[str, Any] | None = None


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
    #: course_added only (Phase 9 D6): the course NUMBER already has a baseline
    #: subject rule in course_requirements (e.g. a re-added course), so the
    #: gate does not ask for one. Computed at read time, never stored.
    subject_rule_exists: bool | None = None


class HandbookChangeListResponse(BaseModel):
    total: int
    counts: dict[str, int]  # e.g. {"pending": 6, "approved": 2, ...}
    items: list[HandbookChangeOut]


class HandbookChangeUpdate(BaseModel):
    """Approve/reject one change. For a course_added the admin supplies the
    university_id + name_en (pre-filled from the book's Uni-Codes section) and
    the stream_codes that decide whether any student can ever see the course.

    Phase 9 D1: approving a course_added REQUIRES stream_codes. The engine only
    serves a course that has a course_stream_eligibility row, so approving
    without one produced a course that was invisible to every student, silently.
    Approved must mean visible.

    Phase 9 D6: approving a course_added also REQUIRES a subject rule — either
    supplied here (validated, written by apply in the same transaction as the
    course) or already existing for the course number. Streams decide who SEES
    the course; the subject rule decides who QUALIFIES. 131's restriction once
    lived only in a free-text note that nothing read — never again."""

    status: Literal["approved", "rejected"]
    notes: str | None = None
    university_id: int | None = Field(default=None, description="required to apply a course_added")
    name_en: str | None = Field(default=None, description="required to apply a course_added")
    stream_codes: list[str] | None = Field(
        default=None,
        description="required to APPROVE a course_added — a course with no stream is invisible to every student",
    )
    subject_rule: dict[str, Any] | None = Field(
        default=None,
        description=(
            "required to APPROVE a course_added unless the course number already "
            "has a baseline rule — the JSON condition tree the engine filters "
            "students on (core/eligibility/subject_requirements.py grammar)"
        ),
    )


class ChangeApplyResponse(BaseModel):
    applied_removed: int
    applied_added: int
    skipped: list[dict[str, Any]]


class CatalogAuditItem(BaseModel):
    """One EXISTING course whose streams differ from what this book says."""

    course_number: str
    name: str | None = None
    book_streams: list[str]
    db_streams: list[str]
    #: the book grants it, we don't -> invisible to students who could apply
    only_in_book: list[str]
    #: we grant it, the book doesn't -> shown to students who cannot apply
    only_in_db: list[str]
    page_number: int | None = None
    #: the book also grants entry by subject list, so its stream list is a
    #: FLOOR — do not "correct" the catalog down to match it here
    book_may_be_incomplete: bool = False
    #: "invisible" (costs a student a degree) or "over_granted"
    severity: str


class AptitudeAuditItem(BaseModel):
    """One course whose aptitude flag contradicts the book's own test table
    (Phase 9.6). Per Uni-Code."""

    course_code: str
    name: str | None = None
    book_requires: bool
    db_requires: bool
    page_number: int | None = None
    #: "unwarned" (book requires a test we never mention — the student loses
    #: their one yearly application) or "over_warned"
    severity: str


class CatalogAuditResponse(BaseModel):
    """Phase 9.3b — the live catalog measured against this handbook.

    Report-only: an admin decides which side is right. Financial Economics/131
    sat wrong for a year because nothing ever ran this comparison."""

    exam_year: int | None = None
    #: how many courses the book documented well enough to compare
    courses_in_book: int
    #: disagreements, worst first (invisible before over_granted)
    items: list[CatalogAuditItem]
    #: aptitude-flag disagreements vs the book's test table (9.6); empty when
    #: the table was unreadable — absence of a comparison is not agreement
    aptitude_items: list[AptitudeAuditItem] = []


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
