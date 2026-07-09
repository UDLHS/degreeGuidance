"""37 stream cutoff overrides

Some courses print ONE official Uni-Code but the handbook's cutoff table
still carries genuinely different z-scores per A/L stream for that same
code (verified across the 2023/2024/2025 books: Food Business Management,
107L, Sabaragamuwa — Commerce Stream vs Biological/Physical Science Stream,
survey found this is the ONLY such course in any of the three books; not a
general schema problem, so this stays a small, additive side-mechanism
rather than reworking z_score_cutoffs for every course).

1. course_stream_cutoff_overrides — one row per (year, course_code,
   district_id, stream_id) that needs a cutoff DIFFERENT from the course's
   general z_score_cutoffs row for that year+district. The general row is
   left NULL for such courses (no single number is honest); eligibility /
   recommendation / chat all fall back to it via COALESCE when no override
   exists for the student's stream, so every other course is unaffected.

2. extraction_columns.override_streams — comma-separated stream codes a
   CONFIRMED column represents when it's a deliberate stream-variant of a
   code another confirmed column in the same run also targets (e.g.
   'COMMERCE' or 'BIO_SCIENCE,PHYSICAL_SCIENCE'). NULL means "the normal
   case" -- a column mapped 1:1 to a code, exactly as before. This is what
   lets the mapping-confirm validation allow >1 confirmed column per code
   when their stream sets are disjoint, instead of always blocking finalize.

Additive only; no existing column, constraint, or row is touched.

Revision ID: eb424f912bbe
Revises: a7b8c9d0e1f2
Create Date: 2026-07-06 20:58:12.893455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb424f912bbe'
down_revision: Union[str, Sequence[str], None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_stream_cutoff_overrides",
        sa.Column("override_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column(
            "course_code", sa.String(15),
            sa.ForeignKey("courses.course_code", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "district_id", sa.Integer,
            sa.ForeignKey("districts.district_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "stream_id", sa.Integer,
            sa.ForeignKey("streams.stream_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("z_score", sa.Numeric(6, 4), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint(
            "year", "course_code", "district_id", "stream_id",
            name="uq_stream_override_year_course_district_stream",
        ),
    )
    op.create_index(
        "idx_stream_override_course_year",
        "course_stream_cutoff_overrides",
        ["course_code", "year"],
    )

    op.add_column(
        "extraction_columns",
        sa.Column(
            "override_streams", sa.String(200), nullable=True,
            comment="comma-separated stream codes this confirmed column represents, "
                    "when it shares its mapped code with another confirmed column "
                    "(disjoint stream split, e.g. 'COMMERCE' / 'BIO_SCIENCE,PHYSICAL_SCIENCE')",
        ),
    )


def downgrade() -> None:
    op.drop_column("extraction_columns", "override_streams")
    op.drop_index("idx_stream_override_course_year", table_name="course_stream_cutoff_overrides")
    op.drop_table("course_stream_cutoff_overrides")
