"""09 courses

Revision ID: 49cd0ba8b89d
Revises: a02798da0bc2
Create Date: 2026-05-20 22:28:50.746556

Creates the courses table and seeds it from data/seeds/courses.csv (261 rows).
All rows are inserted with defaults (selection_basis='district_quota',
requires_aptitude_test=FALSE). Migration 10 will override flags for the
~40 all-island merit Uni-Codes and ~30 aptitude-test Uni-Codes.
"""

import csv
from pathlib import Path

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# KEEP the revision and down_revision lines that Alembic auto-filled above.
# Do not replace them with None.

revision = "49cd0ba8b89d"
down_revision = "a02798da0bc2"
branch_labels = None
depends_on = None



def upgrade():
    op.create_table(
        "courses",
        sa.Column("course_code", sa.String(15), primary_key=True),
        sa.Column("course_number", sa.String(5)),
        sa.Column(
            "university_id",
            sa.Integer,
            sa.ForeignKey("universities.university_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "faculty_id",
            sa.Integer,
            sa.ForeignKey("faculties.faculty_id", ondelete="SET NULL"),
        ),
        sa.Column("name_en", sa.String(300), nullable=False),
        sa.Column("name_si", sa.String(400)),
        sa.Column("name_ta", sa.String(400)),
        sa.Column("degree_type", sa.String(50)),
        sa.Column("duration_years", sa.Numeric(3, 1)),
        sa.Column(
            "selection_basis",
            sa.String(20),
            nullable=False,
            server_default="district_quota",
        ),
        sa.Column(
            "requires_aptitude_test",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("description", sa.Text),
        sa.Column("career_outlook", sa.Text),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("first_intake_year", sa.Integer),
        sa.Column("metadata", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "selection_basis IN ('district_quota', 'all_island_merit')",
            name="ck_courses_selection_basis",
        ),
    )

    # Indexes
    op.create_index("idx_courses_university", "courses", ["university_id"])
    op.create_index(
        "idx_courses_active",
        "courses",
        ["is_active"],
        postgresql_where=sa.text("is_active = TRUE"),
    )
    op.create_index("idx_courses_selection_basis", "courses", ["selection_basis"])
    op.create_index("idx_courses_number", "courses", ["course_number"])

    # Column comments (schema annotations per masterplan §5.2)
    op.execute("""
        COMMENT ON COLUMN courses.selection_basis IS
        'Set via manual seed from handbook Section 1.1 and Section 9 markers. '
        'Not derived from cutoff CSV data — OCR does not capture the * marker.'
    """)
    op.execute("""
        COMMENT ON COLUMN courses.requires_aptitude_test IS
        'Set via manual seed from handbook Section 9 # markers. '
        'Not derived from cutoff CSV data.'
    """)

    # ── Seed data ──────────────────────────────────────────────────────
    csv_path = (
        Path(__file__).resolve().parent.parent.parent
        / "data" / "seeds" / "courses.csv"
    )
    if not csv_path.exists():
        raise RuntimeError(
            f"Seed file not found: {csv_path}. "
            f"Did you copy courses.csv into data/seeds/?"
        )

    conn = op.get_bind()
    uni_rows = conn.execute(sa.text("SELECT university_id, code FROM universities")).fetchall()
    university_ids = {row.code: row.university_id for row in uni_rows}

    rows_to_insert = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uni_code = row["university_code"].strip()
            uid = university_ids.get(uni_code)
            if uid is None:
                raise RuntimeError(
                    f"University code {uni_code!r} not found "
                    f"(needed for course {row['course_code']!r}). "
                    f"Did Phase 2 migration 06_universities run?"
                )
            rows_to_insert.append({
                "course_code": row["course_code"].strip(),
                "course_number": row["course_number"].strip(),
                "university_id": uid,
                "name_en": row["name_en"].strip(),
                "selection_basis": "district_quota",
                "requires_aptitude_test": False,
                "is_active": True,
            })

    op.bulk_insert(
        sa.table(
            "courses",
            sa.column("course_code", sa.String),
            sa.column("course_number", sa.String),
            sa.column("university_id", sa.Integer),
            sa.column("name_en", sa.String),
            sa.column("selection_basis", sa.String),
            sa.column("requires_aptitude_test", sa.Boolean),
            sa.column("is_active", sa.Boolean),
        ),
        rows_to_insert,
    )

    print(f"[migration 09_courses] Seeded {len(rows_to_insert)} courses from CSV.")


def downgrade():
    op.drop_index("idx_courses_number", table_name="courses")
    op.drop_index("idx_courses_selection_basis", table_name="courses")
    op.drop_index("idx_courses_active", table_name="courses")
    op.drop_index("idx_courses_university", table_name="courses")
    op.drop_table("courses")