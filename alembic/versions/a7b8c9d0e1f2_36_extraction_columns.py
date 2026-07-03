"""36 extraction columns + page ranges + staged run statuses

Phase 1 of the handbook pipeline redesign (docs/ADMIN_HANDBOOK_PIPELINE_DESIGN.md).

1. extraction_columns — one row per extracted cutoff-table column per run.
   Holds the raw printed label (2024: Uni-Code; 2025: course name + university),
   the deterministic mapping suggestion, and the admin's confirmed mapping.
   This is the Gate-2 "column -> course" review state.

2. ingestion_runs.cutoff_pages — the confirmed cutoff page ranges as text
   (e.g. "179-188" or "150-156,179-188"), for auditability and re-extraction.

3. Widen chk_run_status with the staged lifecycle states:
   needs_pages   — auto-detection found no parsable cutoff grid; admin must
                   supply the page range.
   needs_mapping — grid extracted; columns await admin mapping confirmation.

Additive only (the constraint swap allows strictly more values).

Revision ID: a7b8c9d0e1f2
Revises: f4a5b6c7d8e9
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = 'a7b8c9d0e1f2'
down_revision = 'f4a5b6c7d8e9'
branch_labels = None
depends_on = None

_OLD_STATUSES = "('running', 'success', 'failed', 'partial')"
_NEW_STATUSES = "('running', 'success', 'failed', 'partial', 'needs_pages', 'needs_mapping')"


def upgrade() -> None:
    op.create_table(
        "extraction_columns",
        sa.Column("column_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ingestion_runs.run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "column_key", sa.String(30), nullable=False,
            comment="stable id within the run, e.g. 'p190.g1.c05'",
        ),
        sa.Column("page_number", sa.Integer, nullable=False),
        sa.Column("raw_label", sa.Text, nullable=False),
        sa.Column(
            "markers", sa.String(10), nullable=True,
            comment="printed flags seen in the label: '#' aptitude, '*' all-island",
        ),
        sa.Column("suggested_course_code", sa.String(15), nullable=True),
        sa.Column("suggestion_confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column(
            "mapped_course_code",
            sa.String(15),
            sa.ForeignKey("courses.course_code", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="pending",
            comment="pending | confirmed | ignored",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('pending', 'confirmed', 'ignored')",
            name="ck_extraction_columns_status",
        ),
        sa.UniqueConstraint("run_id", "column_key", name="uq_extraction_columns_run_key"),
    )
    op.create_index(
        "idx_extraction_columns_run", "extraction_columns", ["run_id", "status"]
    )

    op.add_column("ingestion_runs", sa.Column("cutoff_pages", sa.Text, nullable=True))

    op.drop_constraint("chk_run_status", "ingestion_runs", type_="check")
    op.create_check_constraint("chk_run_status", "ingestion_runs", f"status IN {_NEW_STATUSES}")


def downgrade() -> None:
    # Collapse staged states before tightening the constraint back.
    op.execute(
        "UPDATE ingestion_runs SET status = 'failed' "
        "WHERE status IN ('needs_pages', 'needs_mapping')"
    )
    op.drop_constraint("chk_run_status", "ingestion_runs", type_="check")
    op.create_check_constraint("chk_run_status", "ingestion_runs", f"status IN {_OLD_STATUSES}")

    op.drop_column("ingestion_runs", "cutoff_pages")

    op.drop_index("idx_extraction_columns_run", table_name="extraction_columns")
    op.drop_table("extraction_columns")
