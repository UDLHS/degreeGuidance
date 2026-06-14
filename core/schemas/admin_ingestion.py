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

from pydantic import BaseModel, ConfigDict


class IngestionCreateResponse(BaseModel):
    """Mirror of the ingest_zscores() return dict (handoff §7.2 contract)."""

    run_id: str
    status: str
    processed: int
    failed: int


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
