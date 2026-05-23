"""Cutoff and ingestion observability models — Phase 5.

- ZScoreCutoff: one row per (year, course_code, district_id) cutoff value.
  Populated by the Step 4 ingestion script from reviewed OCR CSVs.

- IngestionRun: per-run accounting (status, counts, who triggered).

- ParseError: triage queue for rows the ingestion couldn't resolve
  (unknown district, unknown course alias, unparseable value).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text as sa_text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class ZScoreCutoff(Base):
    __tablename__ = "z_score_cutoffs"
    __table_args__ = (
        UniqueConstraint("year", "course_code", "district_id", name="uq_zscore_year_course_district"),
        Index(
            "idx_zscore_district_lookup",
            "year", "district_id", "z_score",
            postgresql_where=sa_text("z_score IS NOT NULL"),
        ),
        Index("idx_zscore_course_history", "course_code", "year"),
    )

    cutoff_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    course_code: Mapped[str] = mapped_column(
        String(15),
        ForeignKey("courses.course_code", ondelete="RESTRICT"),
        nullable=False,
    )
    district_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("districts.district_id", ondelete="RESTRICT"),
        nullable=False,
    )
    z_score: Mapped[float | None] = mapped_column(Numeric(6, 4))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'success', 'failed', 'partial')",
            name="chk_run_status",
        ),
    )

    run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa_text("gen_random_uuid()"),
    )
    run_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_label: Mapped[str | None] = mapped_column(String(100))
    year: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_processed: Mapped[int | None] = mapped_column(Integer)
    records_failed: Mapped[int | None] = mapped_column(Integer)
    triggered_by: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    error_log: Mapped[str | None] = mapped_column(Text)


class ParseError(Base):
    __tablename__ = "parse_errors"
    __table_args__ = (
        Index("idx_parse_errors_run", "run_id", "resolved"),
    )

    error_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("ingestion_runs.run_id", ondelete="CASCADE"),
    )
    source_label: Mapped[str | None] = mapped_column(String(100))
    page_number: Mapped[int | None] = mapped_column(Integer)
    raw_block: Mapped[str | None] = mapped_column(Text)
    error_type: Mapped[str | None] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa_text("false"))
    resolved_action: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
