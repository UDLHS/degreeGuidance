"""ORM models for anonymous student chat sessions + the agent's admin-editable
configuration (migration 40)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    student_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    # Admin review marker (migration 39) — toggled from the admin conversations
    # viewer, audited via admin_actions.
    flagged: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    messages: Mapped[list[Message]] = relationship(
        "Message", back_populates="conversation",
        cascade="all, delete-orphan", order_by="Message.created_at",
    )


class AgentConfig(Base):
    """One version of the AI advisor's behavior (migration 40). At most one row
    is active (partial unique index); the orchestrator falls back to its
    built-in prompt when none is. system_prompt_template may contain the
    runtime placeholders {available_years}/{latest_year}/{course_count}/{today}
    — see core/chat/agent_config.py."""

    __tablename__ = "agent_configs"
    __table_args__ = (
        CheckConstraint("max_tool_turns BETWEEN 1 AND 12", name="ck_agent_configs_turns"),
        Index(
            "uq_agent_configs_one_active", "is_active",
            unique=True, postgresql_where=text("is_active"),
        ),
    )

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    web_search_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    max_tool_turns: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("6"))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="ck_messages_role"),
    )

    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
