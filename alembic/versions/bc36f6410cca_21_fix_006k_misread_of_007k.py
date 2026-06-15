"""21_fix_006K_misread_of_007K

Revision ID: bc36f6410cca
Revises: 2ccafb3d723e
Create Date: 2026-06-15 19:08:27.984202

Correct an OCR misread in the 2024 handbook cutoff ingestion.

`006K` is NOT a real Uni-Code: in Section 5 course 006 is "Biological Science"
with university variants 006A-006J only (no K), while "Applied Sciences
(Biological Sc.) — Rajarata" is `007K`. The native_pdf_extractor misread 007K's
rotated code column as `006K` (7->6); it sits in 007K's exact column position
and carries 007K's name + 25 district cutoffs. Migration 16 then wrongly added
`006K` as a separate course, leaving the real catalog course `007K` with zero
cutoffs.

This migration re-homes the cutoffs to `007K` and removes the phantom `006K`
(course + aliases + stream eligibility). The source extraction CSV header was
corrected `006K`->`007K` in the same change so a fresh re-ingestion is also
correct. (The 4 other migration-16 additions — 040R/040W/042L/271D — are genuine
Section-9-only courses and are intentionally left untouched.)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc36f6410cca'
down_revision: Union[str, Sequence[str], None] = '2ccafb3d723e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    if not conn.execute(sa.text("SELECT 1 FROM courses WHERE course_code='006K'")).first():
        return  # already corrected, or 006K never created

    if not conn.execute(sa.text("SELECT 1 FROM courses WHERE course_code='007K'")).first():
        raise RuntimeError("Catalog course 007K is missing; migration 09 must run first.")

    # 007K has no cutoffs of its own, so re-homing 006K's cutoffs cannot collide
    # on the (year, course_code, district_id) unique key.
    n_007k = conn.execute(
        sa.text("SELECT count(*) FROM z_score_cutoffs WHERE course_code='007K'")
    ).scalar_one()
    if n_007k:
        raise RuntimeError(
            f"007K already has {n_007k} cutoffs; aborting to avoid an unexpected merge."
        )

    # 1) Re-home the misread cutoffs to the real catalog course.
    op.execute("UPDATE z_score_cutoffs SET course_code = '007K' WHERE course_code = '006K'")
    # 2) Remove the phantom 006K (FK order: eligibility + aliases before the course).
    op.execute("DELETE FROM course_stream_eligibility WHERE course_code = '006K'")
    op.execute("DELETE FROM course_aliases WHERE course_code = '006K'")
    op.execute("DELETE FROM courses WHERE course_code = '006K'")


def downgrade() -> None:
    conn = op.get_bind()

    if conn.execute(sa.text("SELECT 1 FROM courses WHERE course_code='006K'")).first():
        return  # already restored

    # Recreate the phantom exactly as migrations 16/17 left it, then move the
    # cutoffs back (all of 007K's cutoffs originated from 006K).
    op.execute(
        """
        INSERT INTO courses (course_code, course_number, university_id, name_en,
                             selection_basis, requires_aptitude_test)
        SELECT '006K', '006', u.university_id,
               'Applied Sciences (Bio.Sc) (Rajarata University of Sri Lanka)',
               'district_quota', FALSE
        FROM universities u WHERE u.code = 'RUSL'
        """
    )
    op.execute(
        """
        INSERT INTO course_aliases (course_code, alias_text, source, is_verified)
        VALUES
          ('006K', 'APPLIED SCIENCES (BIO.SC) (RAJARATA UNIVERSITY OF SRI LANKA)',
           'manual_seed_2024_handbook_fix', TRUE),
          ('006K', '006K', 'unicode_self_alias_2024', TRUE)
        """
    )
    op.execute(
        """
        INSERT INTO course_stream_eligibility (course_code, stream_id)
        SELECT '006K', s.stream_id FROM streams s WHERE s.code = 'BIO_SCIENCE'
        """
    )
    op.execute("UPDATE z_score_cutoffs SET course_code = '006K' WHERE course_code = '007K'")
