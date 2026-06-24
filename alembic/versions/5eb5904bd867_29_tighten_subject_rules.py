"""29_tighten_subject_rules

Revision ID: 5eb5904bd867
Revises: f9a59a5bc4bd
Create Date: 2026-06-23 03:05:36.272644

Tightens the 8 course_requirements rows originally seeded (migration 25) as
"needs admin review" approximations, by re-deriving precise logic from the
same §2.2 text already captured this session:

  030 Urban Informatics and Planning   -- exact 1-2-from-A + rest-from-B split
  023 Architecture                     -- exact anchor-subject + secondary-list logic
  097 Landscape Architecture           -- same pattern as Architecture
  092 Tourism & Hospitality Mgmt       -- now stream-conditional (new stream_is
                                          condition type, see subject_requirements.py):
                                          Commerce/BioSci/PhysSci need no extra gate;
                                          Arts needs a specific anchor subject
  098 Translation Studies              -- CORRECTED a real error: the previous
                                          version modeled the Sinhala/Tamil-C gate
                                          as one of two alternate paths (OR'd with
                                          an English-S path that bypassed it). The
                                          C-grade in Sinhala-or-Tamil is mandatory
                                          ALWAYS; English-S is a separate, additional
                                          condition, not a substitute.
  107 Food Business Management         -- now stream-conditional (was a pure
                                          subject-only OR, lost the stream gate)
  109 Business Science                 -- now stream-conditional
  124 Indigenous Pharmaceutical Tech   -- path 1 now stream-conditional

Source of truth is data/seeds/course_requirements_data.py (same module
migration 25 seeded from) -- this migration re-reads it and UPDATEs only the
8 affected course_numbers, not a re-insert.

Downgrade is intentionally a no-op: reverting to a known-less-precise
approximation is not a state worth restoring programmatically.
"""
import sys
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '5eb5904bd867'
down_revision: Union[str, Sequence[str], None] = 'f9a59a5bc4bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TIGHTENED_COURSE_NUMBERS = {"030", "023", "097", "092", "098", "107", "109", "124"}


def upgrade() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(repo_root))
    from data.seeds.course_requirements_data import REQUIREMENTS  # noqa: PLC0415

    by_number = {r["course_number"]: r for r in REQUIREMENTS}
    missing = _TIGHTENED_COURSE_NUMBERS - set(by_number)
    if missing:
        raise RuntimeError(f"Expected tightened entries missing from data module: {missing}")

    table = sa.table(
        "course_requirements",
        sa.column("course_number", sa.String),
        sa.column("exam_year", sa.Integer),
        sa.column("subject_rule", postgresql.JSONB),
        sa.column("ol_requirements", sa.Text),
        sa.column("notes", sa.Text),
    )

    conn = op.get_bind()
    updated = 0
    for course_number in _TIGHTENED_COURSE_NUMBERS:
        r = by_number[course_number]
        stmt = (
            table.update()
            .where(table.c.course_number == course_number)
            .where(table.c.exam_year.is_(None))
            .values(
                subject_rule=r["subject_rule"],
                ol_requirements=r.get("ol_requirements"),
                notes=r.get("notes"),
            )
        )
        result = conn.execute(stmt)
        updated += result.rowcount
    if updated != len(_TIGHTENED_COURSE_NUMBERS):
        raise RuntimeError(
            f"Expected to update {len(_TIGHTENED_COURSE_NUMBERS)} rows, updated {updated}."
        )
    print(f"[migration 29] Tightened {updated} course_requirements rows.")


def downgrade() -> None:
    pass
