"""14 z score cutoffs

Revision ID: 77fc30fc852e
Revises: dd0ebfadeb4b
Create Date: 2026-05-23 09:55:13.317991

Creates the z_score_cutoffs table — the canonical store for handbook
cutoff data. One row per (year, course_code, district_id).

Hot-path index: idx_zscore_district_lookup (partial, where z_score IS NOT NULL)
History index:  idx_zscore_course_history

Populated by apps/worker/jobs/ingest_zscores.py (Step 4 ingestion).
"""

from alembic import op
import sqlalchemy as sa

# KEEP the auto-generated revision/down_revision values above.
revision = "77fc30fc852e"
down_revision = "dd0ebfadeb4b"
branch_labels = None
depends_on = None



def upgrade():
    op.create_table(
        "z_score_cutoffs",
        sa.Column("cutoff_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column(
            "course_code",
            sa.String(15),
            sa.ForeignKey("courses.course_code", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "district_id",
            sa.Integer,
            sa.ForeignKey("districts.district_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("z_score", sa.Numeric(6, 4)),  # NULL = NQC
        sa.Column("notes", sa.Text),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "year", "course_code", "district_id",
            name="uq_zscore_year_course_district",
        ),
    )

    # Hot-path partial index
    op.execute("""
        CREATE INDEX idx_zscore_district_lookup
        ON z_score_cutoffs (year, district_id, z_score)
        WHERE z_score IS NOT NULL
    """)

    # Trend-query index
    op.create_index(
        "idx_zscore_course_history",
        "z_score_cutoffs",
        ["course_code", "year"],
    )

    # Column comments (from masterplan §5.2)
    op.execute("""
        COMMENT ON COLUMN z_score_cutoffs.year IS
        'Academic year of the A/L examination that produced these cutoffs. '
        'NOT the handbook publication year. The 2024/2025 handbook contains '
        'year=2023 cutoffs (from A/L 2023).'
    """)
    op.execute("""
        COMMENT ON COLUMN z_score_cutoffs.z_score IS
        'Z-score range observed in handbook data: approximately [-0.7, +2.9]. '
        'Validator range: [-2.0, +3.0]. NULL = NQC (No Qualified Candidates).'
    """)


def downgrade():
    op.drop_index("idx_zscore_course_history", table_name="z_score_cutoffs")
    op.execute("DROP INDEX IF EXISTS idx_zscore_district_lookup")
    op.drop_table("z_score_cutoffs")
