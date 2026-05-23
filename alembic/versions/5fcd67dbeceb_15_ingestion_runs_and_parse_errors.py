"""15 ingestion runs and parse errors

Revision ID: 5fcd67dbeceb
Revises: 77fc30fc852e
Create Date: 2026-05-23 10:14:10.290773

Operations/observability tables for ingestion jobs.

- ingestion_runs: one row per CSV ingestion (status, counts, who).
- parse_errors: triage queue for rows the ingestion couldn't resolve.

Both tables support admin UI Slice 1 (Week 2) — the admin views run
history at /admin/ingestions and triages parse_errors there.
"""

from alembic import op
import sqlalchemy as sa

# KEEP the auto-generated revision/down_revision values above.
revision = "5fcd67dbeceb"
down_revision = "77fc30fc852e"
branch_labels = None
depends_on = None


def upgrade():
    # Ensure pgcrypto for gen_random_uuid (already enabled with vector extension,
    # but this makes the migration self-contained).
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "ingestion_runs",
        sa.Column(
            "run_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("run_type", sa.String(30), nullable=False),
        sa.Column("source_label", sa.String(100)),
        sa.Column("year", sa.Integer),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("records_processed", sa.Integer),
        sa.Column("records_failed", sa.Integer),
        sa.Column("triggered_by", sa.String(100)),
        sa.Column("notes", sa.Text),
        sa.Column("error_log", sa.Text),
        sa.CheckConstraint(
            "status IN ('running', 'success', 'failed', 'partial')",
            name="chk_run_status",
        ),
    )

    op.create_table(
        "parse_errors",
        sa.Column("error_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "run_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ingestion_runs.run_id", ondelete="CASCADE"),
        ),
        sa.Column("source_label", sa.String(100)),
        sa.Column("page_number", sa.Integer),
        sa.Column("raw_block", sa.Text),
        sa.Column("error_type", sa.String(50)),
        sa.Column("error_message", sa.Text),
        sa.Column(
            "resolved",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("resolved_action", sa.Text),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "idx_parse_errors_run",
        "parse_errors",
        ["run_id", "resolved"],
    )


def downgrade():
    op.drop_index("idx_parse_errors_run", table_name="parse_errors")
    op.drop_table("parse_errors")
    op.drop_table("ingestion_runs")