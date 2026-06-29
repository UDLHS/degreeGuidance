"""Identity + admin-audit + auth-event ORM models.

- User:        admin-sufficient identity row with the role column (migration 19).
- AdminAction: append-only audit trail of admin mutations (migration 19).
- AuthEvent:   append-only login/logout audit trail (migration 20, masterplan §15.2).

Index/constraint definitions mirror the migrations exactly so a future
`alembic --autogenerate` sees no drift.
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
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('student', 'admin', 'superadmin')", name="ck_users_role"
        ),
        Index("idx_users_role", "role", postgresql_where=text("role != 'student'")),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(150))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    google_id: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="student")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class AdminAction(Base):
    __tablename__ = "admin_actions"
    __table_args__ = (
        Index("idx_admin_actions_admin", "admin_user_id", text("created_at DESC")),
        Index("idx_admin_actions_target", "target_table", "target_id"),
        Index("idx_admin_actions_type", "action_type", text("created_at DESC")),
    )

    action_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_table: Mapped[str | None] = mapped_column(String(50))
    target_id: Mapped[str | None] = mapped_column(String(100))
    before_value: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after_value: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class AuthEvent(Base):
    """One row per authentication event. Append-only (masterplan §15.2).

    user_id is nullable + ON DELETE SET NULL so a failed login with an unknown
    email still records (with user_id NULL), and deleting a user preserves their
    historical events.
    """

    __tablename__ = "auth_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('login_success', 'login_failure', 'logout', 'token_refresh')",
            name="ck_auth_events_type",
        ),
        Index("idx_auth_events_user", "user_id", text("created_at DESC")),
        Index("idx_auth_events_email", "email", text("created_at DESC")),
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    email: Mapped[str | None] = mapped_column(String(255))
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
