"""43 articles (admin-authored knowledge beyond courses)

Phase 8.6 of docs/PHASE2_STUDENT_ADMIN_PLAN.md (user request 2026-07-12).
Aptitude-test guides, UGC procedures, scholarship rules, deadlines — indexed
into the chat agent's knowledge base through the same chunk→embed machinery
as factsheets (source_type='article'). content_hash vs the indexed
document_sources.content_hash is the staleness signal, exactly like
factsheets. Additive-only; no seed (articles start empty, admin-authored).

Revision ID: c5d8e2f91a47
Revises: 7fa2c4d81b3e
Create Date: 2026-07-13 00:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c5d8e2f91a47'
down_revision: Union[str, Sequence[str], None] = '7fa2c4d81b3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "articles",
        sa.Column("article_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default=sa.text("1")),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("articles")
