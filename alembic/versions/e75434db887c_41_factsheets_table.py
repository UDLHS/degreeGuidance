"""41 factsheets table (DB becomes the source of truth)

Phase 5 of docs/PHASE2_STUDENT_ADMIN_PLAN.md (decision D3). Factsheet markdown
moves from content/factsheets/*.md into the DB so admins can edit it in
production (the deployed filesystem is ephemeral) with versioning + audit.
The files remain in git as the seed snapshot; this migration loads them.

The RAG indexing job (apps/worker/jobs/index_factsheets.py) reads from this
table from now on; document_sources.content_hash vs factsheets.content_hash
is the staleness signal surfaced in the admin Knowledge/Factsheets pages.

course_number is the natural key (one factsheet per 3-digit course of study,
matching document_sources.course_number). No FK — course numbers are a
derived prefix of courses.course_code, not a table.

Revision ID: e75434db887c
Revises: 093c47d4fb58
Create Date: 2026-07-10 21:13:44.225582
"""
import hashlib
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e75434db887c'
down_revision: Union[str, Sequence[str], None] = '093c47d4fb58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_FACTSHEETS_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "factsheets"


def upgrade() -> None:
    op.create_table(
        "factsheets",
        sa.Column("course_number", sa.String(10), primary_key=True),
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

    # Seed from the git snapshot. Missing directory (a bare prod checkout
    # without content/) seeds nothing — rows can be created via the admin UI.
    if _FACTSHEETS_DIR.exists():
        rows = []
        for path in sorted(_FACTSHEETS_DIR.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            rows.append({
                "course_number": path.stem,
                "content": content,
                "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            })
        if rows:
            op.bulk_insert(
                sa.table(
                    "factsheets",
                    sa.column("course_number", sa.String),
                    sa.column("content", sa.Text),
                    sa.column("content_hash", sa.String),
                ),
                rows,
            )
            print(f"[migration 41] Seeded {len(rows)} factsheets from {_FACTSHEETS_DIR}")


def downgrade() -> None:
    op.drop_table("factsheets")
