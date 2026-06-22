"""Subject-combination prerequisite model (handbook §2.2), Week 3 follow-up.

Keyed by course_number (not course_code) -- the subject rule is defined per
course-of-study type and applies identically across every university offering
it. A course_number with no row is ungated (stream-level check only), so
curation is incremental and never breaks existing behaviour.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class CourseRequirement(Base):
    __tablename__ = "course_requirements"

    requirement_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    course_number: Mapped[str] = mapped_column(String(5), nullable=False)
    exam_year: Mapped[int | None] = mapped_column(Integer)
    subject_rule: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    ol_requirements: Mapped[str | None] = mapped_column(Text)
    source_section: Mapped[str | None] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
