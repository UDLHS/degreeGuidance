"""Reference data models - Phase 2 (Category 1 of three-category population).

These tables hold static UGC/A-L domain knowledge:
-districts: 25 Sri Lankan administrative districs
-streams: 6 A/L streams + ICT navigation category
-subjects: ~30 core A/L subjects
-stream_subjects: which subjects belong to which streams
-mediums: Sinhala / Tamil / English
-universities: 21 state universities + HEIs
-faculties: faculties within universities (populated incrementally)
-special_provision_categories: 6 section-6 admission categories

Seed data livers in Alembic migration files, not here.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from core.models.course import Course


class District(Base):
    __tablename__ = "districts"

    district_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    name_si: Mapped[str | None] = mapped_column(String(100))
    name_ta: Mapped[str | None] = mapped_column(String(100))
    province: Mapped[str | None] = mapped_column(String(50))
    is_disadvantaged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    universities: Mapped[list["University"]] = relationship(back_populates="district")


class Stream(Base):
    __tablename__ = "streams"

    stream_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    name_si: Mapped[str | None] = mapped_column(String(100))
    name_ta: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)


class Subject(Base):
    __tablename__ = "subjects"

    subject_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_si: Mapped[str | None] = mapped_column(String(150))
    name_ta: Mapped[str | None] = mapped_column(String(150))
    is_practical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class StreamSubject(Base):
    __tablename__ = "stream_subjects"

    stream_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("streams.stream_id", ondelete="CASCADE"),
        primary_key=True,
    )
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.subject_id", ondelete="CASCADE"),
        primary_key=True,
    )


class Medium(Base):
    __tablename__ = "mediums"

    medium_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)


class University(Base):
    __tablename__ = "universities"

    university_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(150), nullable=False)
    name_si: Mapped[str | None] = mapped_column(String(200))
    name_ta: Mapped[str | None] = mapped_column(String(200))
    short_name: Mapped[str | None] = mapped_column(String(50))
    district_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("districts.district_id", ondelete="SET NULL"),
    )
    website_url: Mapped[str | None] = mapped_column(Text)
    established: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    district: Mapped["District | None"] = relationship(back_populates="universities")
    faculties: Mapped[list["Faculty"]] = relationship(back_populates="university")
    courses: Mapped[list["Course"]] = relationship(back_populates="university")


class Faculty(Base):
    __tablename__ = "faculties"
    __table_args__ = (
        UniqueConstraint("university_id", "name_en", name="uq_faculty_per_university"),
    )

    faculty_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("universities.university_id", ondelete="CASCADE"),
        nullable=False,
    )
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(50))
    website_url: Mapped[str | None] = mapped_column(Text)

    university: Mapped["University"] = relationship(back_populates="faculties")


class SpecialProvisionCategory(Base):
    __tablename__ = "special_provision_categories"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    handbook_section: Mapped[str | None] = mapped_column(String(20))
