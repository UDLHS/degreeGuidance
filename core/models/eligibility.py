"""ORM models added in Phase 6 (migration 18).

- CourseMedium: junction of courses <-> mediums. Mirrors CourseStreamEligibility.
  Empty until Phase 9 admin work populates it; until then the engine's
  available_mediums comes back as [].
- EligibilityAudit: one row per eligibility query, for forensic investigation
  (masterplan v4 §5.1 item 4).

IMPORTANT — deferred FK:
The masterplan spec for eligibility_audit.user_id is
`UUID REFERENCES users(user_id) ON DELETE SET NULL`. The `users` table does
not exist until Phase 8, so for Phase 6 user_id is a plain nullable UUID with
NO foreign key. The FK constraint is added in the Phase 8 migration that
creates `users`. In Phase 6 (no auth) user_id is always NULL.

Index definitions here intentionally mirror migration 18 so a future
`alembic revision --autogenerate` does not see drift and try to drop them.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class CourseMedium(Base):
    __tablename__ = "course_mediums"

    course_code: Mapped[str] = mapped_column(
        String(15),
        ForeignKey("courses.course_code", ondelete="CASCADE"),
        primary_key=True,
    )
    medium_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mediums.medium_id"),
        primary_key=True,
    )


class EligibilityAudit(Base):
    __tablename__ = "eligibility_audit"
    __table_args__ = (
        # Matches migration 18 exactly.
        Index("idx_eligibility_audit_user", "user_id", text("created_at DESC")),
        Index("idx_eligibility_audit_hash", "request_hash"),
    )

    audit_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # FK to users(user_id) deferred to Phase 8 (users table does not exist yet).
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )

    z_score: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    district_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("districts.district_id"), nullable=False
    )
    stream_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("streams.stream_id"), nullable=False
    )
    cutoff_year_used: Mapped[int] = mapped_column(Integer, nullable=False)
    eligible_count: Mapped[int] = mapped_column(Integer, nullable=False)
    conditional_count: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    result_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
