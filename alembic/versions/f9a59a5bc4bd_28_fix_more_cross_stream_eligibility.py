"""28_fix_more_cross_stream_eligibility

Revision ID: f9a59a5bc4bd
Revises: 2ae50003b4ee
Create Date: 2026-06-23 02:45:16.632798

Continuation of migration 26's correction. While tightening the
course_requirements subject rules for the 8 "needs admin review" courses,
checked every course with a stream-restricting §2.2.8 note against the live
DB and found 6 MORE courses still over-inclusive (set to all 6 streams as the
migration-12 MVP placeholder):

  027D Management and Information Technology (MIT)     -> BIO_SCIENCE, PHYSICAL_SCIENCE
  109G Business Science                                  -> PHYSICAL_SCIENCE, COMMERCE
  111B Geographical Information Science                  -> ARTS, BIO_SCIENCE, PHYSICAL_SCIENCE
  121P Health Information and Communication Technology   -> ENGINEERING_TECH, BIOSYSTEMS_TECH
  123P Biomedical Technology                              -> ENGINEERING_TECH, BIOSYSTEMS_TECH
  124P Indigenous Pharmaceutical Technology               -> ENGINEERING_TECH, BIOSYSTEMS_TECH,
                                                              BIO_SCIENCE, PHYSICAL_SCIENCE

(107L Food Business Management and 271D MIT-BioScience-variant were already
correct -- verified, not assumed. 122P was already corrected in migration 26.)

Source: handbook 2024/2025 §2.2.8.2/.31/.33/.36/.38/.39, read in full this
session; course_requirements.subject_rule (migration 25/this session) now also
encodes the within-stream subject specificity via the new stream_is condition
type for the courses whose rule genuinely differs by stream.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f9a59a5bc4bd'
down_revision: Union[str, Sequence[str], None] = '2ae50003b4ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_CORRECTIONS = {
    "027D": ["BIO_SCIENCE", "PHYSICAL_SCIENCE"],
    "109G": ["PHYSICAL_SCIENCE", "COMMERCE"],
    "111B": ["ARTS", "BIO_SCIENCE", "PHYSICAL_SCIENCE"],
    "121P": ["ENGINEERING_TECH", "BIOSYSTEMS_TECH"],
    "123P": ["ENGINEERING_TECH", "BIOSYSTEMS_TECH"],
    "124P": ["ENGINEERING_TECH", "BIOSYSTEMS_TECH", "BIO_SCIENCE", "PHYSICAL_SCIENCE"],
}

_ALL_SIX = [
    "ARTS", "COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE",
    "ENGINEERING_TECH", "BIOSYSTEMS_TECH",
]


def _apply(conn, mapping: dict[str, list[str]]) -> None:
    stream_ids = {
        row.code: row.stream_id
        for row in conn.execute(sa.text("SELECT stream_id, code FROM streams")).fetchall()
    }
    for course_code, stream_codes in mapping.items():
        conn.execute(
            sa.text("DELETE FROM course_stream_eligibility WHERE course_code = :cc"),
            {"cc": course_code},
        )
        for sc in stream_codes:
            sid = stream_ids.get(sc)
            if sid is None:
                raise RuntimeError(f"Stream code {sc!r} not found (needed for {course_code!r}).")
            conn.execute(
                sa.text(
                    "INSERT INTO course_stream_eligibility (course_code, stream_id) "
                    "VALUES (:cc, :sid)"
                ),
                {"cc": course_code, "sid": sid},
            )


def upgrade() -> None:
    conn = op.get_bind()
    _apply(conn, _CORRECTIONS)
    total = sum(len(v) for v in _CORRECTIONS.values())
    print(f"[migration 28] Corrected stream eligibility for {len(_CORRECTIONS)} courses ({total} rows).")


def downgrade() -> None:
    conn = op.get_bind()
    _apply(conn, {code: _ALL_SIX for code in _CORRECTIONS})
