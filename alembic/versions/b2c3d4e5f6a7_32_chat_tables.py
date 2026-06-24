"""32 chat tables — conversations and messages

Week 5 chatbot. Anonymous conversations keyed by a browser-generated
session_id; messages stored with role and content; tool_calls logged
as JSONB on the assistant message row for auditability.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("session_id", sa.String(64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
    )
    op.execute("CREATE INDEX idx_conversations_session ON conversations (session_id, updated_at DESC)")

    op.create_table(
        "messages",
        sa.Column("message_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role", sa.String(20), nullable=False,
            comment="'user' | 'assistant' | 'system'",
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("tool_calls", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name="ck_messages_role"),
    )
    op.execute("CREATE INDEX idx_messages_conversation ON messages (conversation_id, created_at)")


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("conversations")
