"""Course eligibility and alias models — Phase 4 (Category 2 of three-category population).

- CourseStreamEligibility: which A/L streams may apply for which course.
  Pure composite PK (course_code, stream_id). One row per (course, stream).

- CourseAlias: bridges OCR labels (e.g., 'MEDICINE (University of Colombo)')
  to course_codes (e.g., '001A'). Day 5 z-score ingestion resolves
  CSV column headers via this table.
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class CourseStreamEligibility(Base):
    __tablename__ = "course_stream_eligibility"

    course_code: Mapped[str] = mapped_column(
        String(15),
        ForeignKey("courses.course_code", ondelete="CASCADE"),
        primary_key=True,
    )
    stream_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("streams.stream_id"),
        primary_key=True,
    )


class CourseAlias(Base):
    __tablename__ = "course_aliases"
    __table_args__ = (
        UniqueConstraint("alias_text", "course_code", name="uq_alias_per_course"),
        Index("idx_aliases_course", "course_code"),
    )

    alias_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_code: Mapped[str] = mapped_column(
        String(15),
        ForeignKey("courses.course_code", ondelete="CASCADE"),
        nullable=False,
    )
    alias_text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(50))
    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2))
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
