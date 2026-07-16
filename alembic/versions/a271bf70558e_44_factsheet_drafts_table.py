"""44 factsheet drafts table (Phase 9.4 — book-first drafts, human-gated)

A machine-written factsheet lands HERE, never in factsheets: the RAG index job
reads the factsheets table and nothing else, so an unreviewed draft is
structurally incapable of reaching the AI advisor (decision D4 — never index
unreviewed text). Approval copies the text into factsheets through the same
versioned/audited/auto-reindexed path as a hand edit.

One row per 3-digit course number (same natural key as factsheets, and same
no-FK reasoning: course numbers are a derived prefix of courses.course_code).
Lifecycle: queued → ready | failed; rejected keeps the row so the page can say
what happened; approve deletes it; a new generation replaces it.

Revision ID: a271bf70558e
Revises: c5d8e2f91a47
Create Date: 2026-07-16 20:43:51.308112
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a271bf70558e'
down_revision: Union[str, Sequence[str], None] = 'c5d8e2f91a47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "factsheet_drafts",
        sa.Column("course_number", sa.String(10), primary_key=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'queued'")),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("provenance", postgresql.JSONB, nullable=True),
        sa.Column(
            "requested_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'ready', 'failed', 'rejected')",
            name="ck_factsheet_drafts_status",
        ),
    )


def downgrade() -> None:
    op.drop_table("factsheet_drafts")
