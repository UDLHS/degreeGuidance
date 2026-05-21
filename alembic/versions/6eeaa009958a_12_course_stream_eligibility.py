"""12 course stream eligibility

Revision ID: 6eeaa009958a
Revises: 25d1beea7023
Create Date: 2026-05-21 19:04:28.059448

Creates course_stream_eligibility table and seeds it from
data/seeds/course_stream_eligibility.csv (611 rows).

Stream mapping per handbook §2.2:
- §2.2.1 Arts Stream (17 course_numbers)
- §2.2.2 Commerce Stream (9 course_numbers)
- §2.2.3 Biological Science Stream (37 course_numbers)
- §2.2.4 Physical Science Stream (13 course_numbers)
- §2.2.5 Engineering Technology Stream (102 only)
- §2.2.6 Biosystems Technology Stream (103 only)
- §2.2.7 + §2.2.8 Cross-stream (48 course_numbers, all 6 streams each)

For MVP, cross-stream courses are assigned to ALL 6 streams. Precise
per-course subject prerequisites are deferred to the §2.2 parser
(Phase 2 per masterplan v4 §8.4).
"""

import csv
from pathlib import Path

from alembic import op
import sqlalchemy as sa

# KEEP the auto-generated revision and down_revision values above.
revision = "6eeaa009958a"
down_revision = "25d1beea7023"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "course_stream_eligibility",
        sa.Column(
            "course_code",
            sa.String(15),
            sa.ForeignKey("courses.course_code", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "stream_id",
            sa.Integer,
            sa.ForeignKey("streams.stream_id"),
            primary_key=True,
        ),
    )

    # Seed from CSV
    csv_path = (
        Path(__file__).resolve().parent.parent.parent
        / "data" / "seeds" / "course_stream_eligibility.csv"
    )
    if not csv_path.exists():
        raise RuntimeError(
            f"Seed file not found: {csv_path}. "
            f"Did you copy course_stream_eligibility.csv into data/seeds/?"
        )

    conn = op.get_bind()
    stream_rows = conn.execute(sa.text("SELECT stream_id, code FROM streams")).fetchall()
    stream_ids = {row.code: row.stream_id for row in stream_rows}

    rows_to_insert = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stream_code = row["stream_code"].strip()
            sid = stream_ids.get(stream_code)
            if sid is None:
                raise RuntimeError(
                    f"Stream code {stream_code!r} not found "
                    f"(needed for course {row['course_code']!r}). "
                    f"Did Phase 2 migration 02_streams run?"
                )
            rows_to_insert.append({
                "course_code": row["course_code"].strip(),
                "stream_id": sid,
            })

    op.bulk_insert(
        sa.table(
            "course_stream_eligibility",
            sa.column("course_code", sa.String),
            sa.column("stream_id", sa.Integer),
        ),
        rows_to_insert,
    )

    print(f"[migration 12] Seeded {len(rows_to_insert)} eligibility rows.")


def downgrade():
    op.drop_table("course_stream_eligibility")