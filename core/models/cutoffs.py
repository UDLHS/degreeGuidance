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
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
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


class CourseStreamCutoffOverride(Base):
    """A cutoff for (course, district, year) that differs by A/L stream.

    Only populated for the rare course whose handbook cutoff table carries
    genuinely different z-scores per stream under ONE official Uni-Code
    (verified: Food Business Management/107L is the only such case across
    the 2023/2024/2025 books). ZScoreCutoff.z_score is left NULL for these
    (course, district, year) rows -- callers COALESCE this table's value (for
    the student's own stream) over the general row, so every other course's
    query path is untouched.
    """

    __tablename__ = "course_stream_cutoff_overrides"
    __table_args__ = (
        UniqueConstraint(
            "year", "course_code", "district_id", "stream_id",
            name="uq_stream_override_year_course_district_stream",
        ),
        Index("idx_stream_override_course_year", "course_code", "year"),
    )

    override_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
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
    stream_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("streams.stream_id", ondelete="RESTRICT"),
        nullable=False,
    )
    z_score: Mapped[float | None] = mapped_column(Numeric(6, 4))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class UnmappedCutoff(Base):
    """A cutoff-table column preserved WITHOUT a Uni-Code — real z-scores that
    have no code in the book's Uni-Code section (a discontinued/renamed course
    still printing its own cutoff column). Kept verbatim by printed label so
    the data is never lost; not joined into course_code-keyed eligibility.
    See migration 38 and [[handbook-format-knowledge]]."""

    __tablename__ = "unmapped_cutoffs"
    __table_args__ = (
        UniqueConstraint("year", "raw_label", "district_id", name="uq_unmapped_year_label_district"),
        Index("idx_unmapped_year", "year"),
    )

    unmapped_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("ingestion_runs.run_id", ondelete="SET NULL")
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_label: Mapped[str] = mapped_column(Text, nullable=False)
    course_name: Mapped[str | None] = mapped_column(Text)
    university: Mapped[str | None] = mapped_column(Text)
    district_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("districts.district_id", ondelete="RESTRICT"), nullable=False
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
            "status IN ('running', 'success', 'failed', 'partial', "
            "'needs_pages', 'needs_mapping')",
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
    cutoff_pages: Mapped[str | None] = mapped_column(
        Text, comment="confirmed cutoff page ranges, e.g. '179-188' or '150-156,179-188'"
    )


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


class ExtractionColumn(Base):
    """One extracted cutoff-table column awaiting (or holding) its course mapping.

    raw_label is whatever the book printed for the column: a Uni-Code in
    2024-style books, or 'COURSE NAME (University …)' in 2025-style books.
    The admin confirms mapped_course_code at Gate 2; suggestions are
    deterministic (aliases + name similarity), never LLM-invented.
    """

    __tablename__ = "extraction_columns"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'ignored', 'unmapped_kept')",
            name="ck_extraction_columns_status",
        ),
        UniqueConstraint("run_id", "column_key", name="uq_extraction_columns_run_key"),
        Index("idx_extraction_columns_run", "run_id", "status"),
    )

    column_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("ingestion_runs.run_id", ondelete="CASCADE"),
        nullable=False,
    )
    column_key: Mapped[str] = mapped_column(String(30), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_label: Mapped[str] = mapped_column(Text, nullable=False)
    markers: Mapped[str | None] = mapped_column(String(10))
    suggested_course_code: Mapped[str | None] = mapped_column(String(15))
    suggestion_confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))
    mapped_course_code: Mapped[str | None] = mapped_column(
        String(15), ForeignKey("courses.course_code", ondelete="RESTRICT"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=sa_text("'pending'"))
    override_streams: Mapped[str | None] = mapped_column(
        String(200),
        comment="comma-separated stream codes this column represents when it "
                "shares its mapped code with another confirmed column (disjoint "
                "stream split); NULL is the normal 1:1 case",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class HandbookChange(Base):
    """One reviewable difference between an extracted handbook and the live DB.

    Produced by the diff stage after a pdf_extraction run. 'course_added' and
    'course_removed' drive real course-table mutations on approval; 'cutoff_changed'
    is an observability report (the numbers promote through the Step-4 loader).
    """

    __tablename__ = "handbook_changes"
    __table_args__ = (
        CheckConstraint(
            "change_type IN ('course_added', 'course_removed', 'cutoff_changed')",
            name="ck_handbook_changes_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'applied')",
            name="ck_handbook_changes_status",
        ),
        Index("idx_handbook_changes_run", "run_id", "status"),
    )

    change_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("ingestion_runs.run_id", ondelete="CASCADE"),
        nullable=False,
    )
    change_type: Mapped[str] = mapped_column(String(20), nullable=False)
    course_code: Mapped[str] = mapped_column(String(15), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    before_value: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after_value: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=sa_text("'pending'")
    )
    resolved_by: Mapped[str | None] = mapped_column(String(100))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
