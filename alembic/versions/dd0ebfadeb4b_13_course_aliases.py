"""13 course aliases

Revision ID: dd0ebfadeb4b
Revises: 6eeaa009958a
Create Date: 2026-05-21 19:07:25.286649

Creates course_aliases table and seeds it from
data/seeds/course_aliases.csv (261 rows).

Each alias maps an OCR-format label (e.g., 'MEDICINE (University of Colombo)')
to a course_code ('001A'). This is the bridge Day 5's z-score ingestion uses
to resolve CSV column headers from your Step 2 OCR output.

All seed aliases are marked is_verified=TRUE because they're derived
from the handbook Section 5 Uni-Code list (canonical source).
"""

import csv
from pathlib import Path

from alembic import op
import sqlalchemy as sa

# KEEP the auto-generated revision and down_revision values above.
revision = "dd0ebfadeb4b"
down_revision = "6eeaa009958a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "course_aliases",
        sa.Column("alias_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "course_code",
            sa.String(15),
            sa.ForeignKey("courses.course_code", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("alias_text", sa.Text, nullable=False),
        sa.Column("source", sa.String(50)),
        sa.Column("confidence", sa.Numeric(3, 2)),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("alias_text", "course_code", name="uq_alias_per_course"),
    )

    # Indexes
    op.create_index("idx_aliases_course", "course_aliases", ["course_code"])
    # GIN full-text index on alias_text (for fuzzy lookups in admin UI)
    op.execute("""
        CREATE INDEX idx_aliases_text
        ON course_aliases USING gin(to_tsvector('english', alias_text))
    """)

    # Seed from CSV
    csv_path = (
        Path(__file__).resolve().parent.parent.parent
        / "data" / "seeds" / "course_aliases.csv"
    )
    if not csv_path.exists():
        raise RuntimeError(
            f"Seed file not found: {csv_path}. "
            f"Did you copy course_aliases.csv into data/seeds/?"
        )

    rows_to_insert = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_to_insert.append({
                "course_code": row["course_code"].strip(),
                "alias_text": row["alias_text"].strip(),
                "source": row["source"].strip(),
                "confidence": float(row["confidence"]),
                "is_verified": row["is_verified"].strip().upper() == "TRUE",
            })

    op.bulk_insert(
        sa.table(
            "course_aliases",
            sa.column("course_code", sa.String),
            sa.column("alias_text", sa.Text),
            sa.column("source", sa.String),
            sa.column("confidence", sa.Numeric),
            sa.column("is_verified", sa.Boolean),
        ),
        rows_to_insert,
    )

    print(f"[migration 13] Seeded {len(rows_to_insert)} aliases.")


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_aliases_text")
    op.drop_index("idx_aliases_course", table_name="course_aliases")
    op.drop_table("course_aliases")
