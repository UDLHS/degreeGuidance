"""35 handbook change-set

Phase A1 of the admin handbook-sync pipeline. After a handbook PDF is extracted,
a diff stage compares the extracted course-code set + cutoffs against the current
DB and records each difference here for admin review:

- course_added   : a Uni-Code in the new book absent from the courses table
- course_removed : an active course whose code is absent from the new book
- cutoff_changed : a course whose z-scores moved vs the latest prior year

Rows are 'pending' until an admin approves/rejects. Approved added/removed
changes are applied to the courses table (added -> inactive stub the admin
completes; removed -> is_active = false, retained for chat/history). The cutoff
numbers themselves still flow through the existing Step-4 promote; cutoff_changed
rows are an observability report, not a per-cell approval queue.

Additive only: one new table, no change to any existing table.

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-06-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = 'f4a5b6c7d8e9'
down_revision = 'e3f4a5b6c7d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "handbook_changes",
        sa.Column("change_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ingestion_runs.run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("change_type", sa.String(20), nullable=False),
        sa.Column("course_code", sa.String(15), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("before_value", postgresql.JSONB, nullable=True),
        sa.Column("after_value", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("resolved_by", sa.String(100), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "change_type IN ('course_added', 'course_removed', 'cutoff_changed')",
            name="ck_handbook_changes_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'applied')",
            name="ck_handbook_changes_status",
        ),
    )
    op.create_index(
        "idx_handbook_changes_run", "handbook_changes", ["run_id", "status"]
    )


def downgrade() -> None:
    op.drop_index("idx_handbook_changes_run", table_name="handbook_changes")
    op.drop_table("handbook_changes")
