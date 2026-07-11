"""42 ingestion_artifacts (cross-instance artifact store)

W2 follow-through of docs/PHASE2_STUDENT_ADMIN_PLAN.md. Production runs the
API and the Arq worker as separate Render services with separate ephemeral
disks, so the work-dir files the staged PDF pipeline passes between stages
(pdf / grid.json / presence.json / csv / overrides.json / unmapped.json)
never reach the other process — and don't even survive a deploy on the same
one. This table is the durable copy; the work dir becomes a cache
(core/ingestion/artifact_store.py). Also serves as the permanent per-year
retention of the raw handbook and the promoted CSV, plus the pre-promote
snapshot_*.csv safety dumps that make every promote reversible in prod.

Additive-only; rows cascade with their ingestion run.

Revision ID: 7fa2c4d81b3e
Revises: e75434db887c
Create Date: 2026-07-11 12:05:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7fa2c4d81b3e'
down_revision: Union[str, Sequence[str], None] = 'e75434db887c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ingestion_artifacts",
        sa.Column("artifact_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ingestion_runs.run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("content", sa.LargeBinary, nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("run_id", "kind", name="uq_artifact_run_kind"),
    )
    op.create_index("idx_artifacts_run", "ingestion_artifacts", ["run_id"])


def downgrade() -> None:
    op.drop_index("idx_artifacts_run", table_name="ingestion_artifacts")
    op.drop_table("ingestion_artifacts")
