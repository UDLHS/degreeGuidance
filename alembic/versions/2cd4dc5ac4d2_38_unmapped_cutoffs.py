"""38 unmapped (codeless) cutoffs

A cutoff-table column can carry real z-scores while having NO Uni-Code in the
book's Uni-Code section (e.g. a course being discontinued/renamed — 2023
"Computing & Information Systems" at Sabaragamuwa, which the book merges into
"Information Systems" 096L but still prints its own cutoff column). Such data
must never be discarded and must never be force-fitted onto another course's
code. This stores it verbatim, keyed by the printed label instead of a code.

1. unmapped_cutoffs — one row per (year, printed label, district) with the
   z-score. Preserved for the record and for the chat agent's historical /
   statistical use. It is NOT joined into student eligibility/recommendations
   (that engine is course_code-keyed; there is no course to recommend), by
   design. Separate from z_score_cutoffs — the working cutoff flow is untouched.

2. extraction_columns.status gains 'unmapped_kept' — the admin's deliberate
   "this has data but no Uni-Code, keep it as-is" choice, distinct from
   'confirmed' (has a code) and 'ignored' (dropped). Additive constraint swap.

Revision ID: 2cd4dc5ac4d2
Revises: eb424f912bbe
Create Date: 2026-07-07 18:45:49.626427
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2cd4dc5ac4d2'
down_revision: Union[str, Sequence[str], None] = 'eb424f912bbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_OLD_COL_STATUS = "('pending', 'confirmed', 'ignored')"
_NEW_COL_STATUS = "('pending', 'confirmed', 'ignored', 'unmapped_kept')"


def upgrade() -> None:
    op.create_table(
        "unmapped_cutoffs",
        sa.Column("unmapped_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ingestion_runs.run_id", ondelete="SET NULL"),
            nullable=True,
            comment="provenance; SET NULL so the cutoff persists past a run delete, like z_score_cutoffs",
        ),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column(
            "raw_label", sa.Text, nullable=False,
            comment="the printed cutoff-column label, verbatim (identity when there is no code)",
        ),
        sa.Column("course_name", sa.Text, nullable=True),
        sa.Column("university", sa.Text, nullable=True),
        sa.Column(
            "district_id", sa.Integer,
            sa.ForeignKey("districts.district_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("z_score", sa.Numeric(6, 4), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("year", "raw_label", "district_id", name="uq_unmapped_year_label_district"),
    )
    op.create_index("idx_unmapped_year", "unmapped_cutoffs", ["year"])

    op.drop_constraint("ck_extraction_columns_status", "extraction_columns", type_="check")
    op.create_check_constraint(
        "ck_extraction_columns_status", "extraction_columns", f"status IN {_NEW_COL_STATUS}"
    )


def downgrade() -> None:
    op.execute("UPDATE extraction_columns SET status = 'ignored' WHERE status = 'unmapped_kept'")
    op.drop_constraint("ck_extraction_columns_status", "extraction_columns", type_="check")
    op.create_check_constraint(
        "ck_extraction_columns_status", "extraction_columns", f"status IN {_OLD_COL_STATUS}"
    )

    op.drop_index("idx_unmapped_year", table_name="unmapped_cutoffs")
    op.drop_table("unmapped_cutoffs")
