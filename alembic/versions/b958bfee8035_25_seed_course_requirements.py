"""25_seed_course_requirements

Revision ID: b958bfee8035
Revises: df0357f343ce
Create Date: 2026-06-22 17:41:40.223700

Seeds course_requirements from data/seeds/course_requirements_data.py (125
rows), hand-transcribed from a full read of the 2024/2025 handbook's
Section 2.2 (every subsection, 2.2.1 through 2.2.8). Keyed by course_number.

Arts (course_number 019) and the 3 Section-9-only specials (040, 042, 271 --
flagged in migration 16/the project's prior data-integrity work as having
unverified codes with no dedicated §2.2 entry) are deliberately NOT seeded
here -- they remain ungated (stream-level check only) rather than encode
subject logic not grounded in real handbook text. Arts gets its own basket
checker in a follow-up change.
"""

import sys
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b958bfee8035'
down_revision: Union[str, Sequence[str], None] = 'df0357f343ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    data_path = repo_root / "data" / "seeds" / "course_requirements_data.py"
    if not data_path.exists():
        raise RuntimeError(f"Seed file not found: {data_path}")

    sys.path.insert(0, str(repo_root))
    from data.seeds.course_requirements_data import REQUIREMENTS  # noqa: PLC0415

    table = sa.table(
        "course_requirements",
        sa.column("course_number", sa.String),
        sa.column("exam_year", sa.Integer),
        sa.column("subject_rule", postgresql.JSONB),
        sa.column("ol_requirements", sa.Text),
        sa.column("source_section", sa.String),
        sa.column("notes", sa.Text),
    )
    rows = [
        {
            "course_number": r["course_number"],
            "exam_year": r.get("exam_year"),
            "subject_rule": r["subject_rule"],
            "ol_requirements": r.get("ol_requirements"),
            "source_section": r.get("source_section"),
            "notes": r.get("notes"),
        }
        for r in REQUIREMENTS
    ]
    op.bulk_insert(table, rows)
    print(f"[migration 25] Seeded {len(rows)} course_requirements rows.")


def downgrade() -> None:
    op.execute("DELETE FROM course_requirements")
