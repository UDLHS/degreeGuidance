"""39 conversation flagged (admin review marker)

Phase 2 of docs/PHASE2_STUDENT_ADMIN_PLAN.md — the admin conversations viewer
needs a way to mark a student chat for review (bad/over-confident advice, a
question worth a factsheet fix, etc.). One additive boolean; flag changes are
audited via admin_actions like every other admin mutation.

Revision ID: 985e13967bd9
Revises: 2cd4dc5ac4d2
Create Date: 2026-07-10 17:23:46.026798
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '985e13967bd9'
down_revision: Union[str, Sequence[str], None] = '2cd4dc5ac4d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column(
            "flagged", sa.Boolean, nullable=False, server_default=sa.text("false"),
            comment="admin marked this conversation for review",
        ),
    )


def downgrade() -> None:
    op.drop_column("conversations", "flagged")
