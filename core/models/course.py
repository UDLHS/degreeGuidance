"""Course model — Phase 3 (Category 2 of three-category population).

The `courses` table holds the 261 UGC Uni-Codes (course-university pairs).
Seed data lives in `data/seeds/courses.csv` and is loaded by migration 09_courses.
Special markers (`*` all-island merit, `#` aptitude test) are applied in migration 10.

course_code is the natural PRIMARY KEY (the UGC Uni-Code, e.g., '001A').
course_number is the 3-digit course-of-study identifier (e.g., '001').
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint(
            "selection_basis IN ('district_quota', 'all_island_merit')",
            name="ck_courses_selection_basis",
        ),
        Index("idx_courses_university", "university_id"),
        Index("idx_courses_active", "is_active", postgresql_where="is_active = TRUE"),
        Index("idx_courses_selection_basis", "selection_basis"),
        Index("idx_courses_number", "course_number"),
    )

    course_code: Mapped[str] = mapped_column(String(15), primary_key=True)
    course_number: Mapped[str | None] = mapped_column(String(5))

    university_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("universities.university_id", ondelete="RESTRICT"),
        nullable=False,
    )
    faculty_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("faculties.faculty_id", ondelete="SET NULL"),
    )

    name_en: Mapped[str] = mapped_column(String(300), nullable=False)
    name_si: Mapped[str | None] = mapped_column(String(400))
    name_ta: Mapped[str | None] = mapped_column(String(400))

    degree_type: Mapped[str | None] = mapped_column(String(50))
    duration_years: Mapped[float | None] = mapped_column(Numeric(3, 1))

    selection_basis: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="district_quota",
    )
    requires_aptitude_test: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )

    description: Mapped[str | None] = mapped_column(Text)
    career_outlook: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    first_intake_year: Mapped[int | None] = mapped_column(Integer)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    university: Mapped["University"] = relationship(back_populates="courses")  # type: ignore[name-defined]
    faculty: Mapped["Faculty | None"] = relationship()  # type: ignore[name-defined]
