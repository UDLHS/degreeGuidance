"""30_seed_special_course_requirements

Revision ID: 5b7bc34e2628
Revises: 5eb5904bd867
Create Date: 2026-06-23 10:28:05.628659

Seeds course_requirements for the 3 "Section-9-only" specials that migration
25 deliberately left ungated (040, 042, 271 -- flagged back then as having no
dedicated §2.2 entry, so left unencoded rather than guessed).

Went back to the primary source this session and found each is in fact the
same programme as an existing, fully-documented base course, just a separate
cutoff-tracking code for a stream-specific intake split explicitly described
in that base course's §2.2 text:

  040 Management Studies (TV) - B  -> same as course 022 (§2.2.2.5): "any
      three subjects... are eligible", no stream restriction. The 60%/40%
      Commerce split mentioned there is a selection quota, not a gate.
  042 Arts (SAB) - B               -> same as course 021 (§2.2.1.1.2):
      "Arts Stream or Commerce Stream", no further subject specificity.
      042 is specifically the Commerce-quota-origin cutoff track.
  271 MIT (Bio Science Stream)     -> same as course 027 (§2.2.8.2), which
      explicitly states "40% of intake from Biological Science Stream" is
      selected separately. 271 is that 40% quota's cutoff-tracking code at
      the same university (Kelaniya). Subject rule mirrors 027's exactly.

In all 3 cases course_stream_eligibility was independently checked against
the live DB and confirmed already correct (not touched by this migration).
"""

import sys
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '5b7bc34e2628'
down_revision: Union[str, Sequence[str], None] = '5eb5904bd867'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW_COURSE_NUMBERS = {"040", "042", "271"}


def upgrade() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(repo_root))
    from data.seeds.course_requirements_data import REQUIREMENTS  # noqa: PLC0415

    by_number = {r["course_number"]: r for r in REQUIREMENTS}
    missing = _NEW_COURSE_NUMBERS - set(by_number)
    if missing:
        raise RuntimeError(f"Expected entries missing from data module: {missing}")

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
        for cn in _NEW_COURSE_NUMBERS
        for r in [by_number[cn]]
    ]
    op.bulk_insert(table, rows)
    print(f"[migration 30] Seeded {len(rows)} course_requirements rows (040, 042, 271).")


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DELETE FROM course_requirements WHERE course_number = ANY(:numbers) "
            "AND exam_year IS NULL"
        ),
        {"numbers": list(_NEW_COURSE_NUMBERS)},
    )
