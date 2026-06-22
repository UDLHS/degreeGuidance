"""26_fix_cross_stream_eligibility_overreach

Revision ID: 66e1fd4b50a7
Revises: b958bfee8035
Create Date: 2026-06-22 18:17:05.731021

Migration 12's own comment documents that cross-stream courses were
deliberately set to ALL 6 streams "for MVP... precise per-course subject
prerequisites are deferred to the §2.2 parser (Phase 2)" -- this is that
Phase 2 work. Having now read the actual §2.2.8 text for these 5 courses,
the real stream sets are narrower than "all 6":

  066U Entrepreneurship and Management            -> Commerce, BioSci, PhysSci
  090U Hospitality, Tourism and Events Management  -> Commerce, BioSci, PhysSci
  092K/092L Tourism & Hospitality Management        -> Commerce, BioSci, PhysSci, Arts
                                                       (Arts path requires >=1 of
                                                       {Economics,Geography,Business
                                                       Statistics} + 2 more Arts
                                                       subjects -- enforced by
                                                       course_requirements.subject_rule
                                                       for course_number 092, not here)
  107L Food Business Management                    -> Commerce, BioSci, PhysSci
  122P Health Tourism and Hospitality Management    -> Commerce, BioSci, PhysSci,
                                                       EngineeringTech, BiosystemsTech
                                                       (NOT Arts)

Source: handbook 2024/2025 §2.2.8.15/.18/.22/.29/.37, read in full this session.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '66e1fd4b50a7'
down_revision: Union[str, Sequence[str], None] = 'b958bfee8035'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# course_code -> correct stream codes (per the real §2.2.8 text)
_CORRECTIONS = {
    "066U": ["COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE"],
    "090U": ["COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE"],
    "092K": ["COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE", "ARTS"],
    "092L": ["COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE", "ARTS"],
    "107L": ["COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE"],
    "122P": ["COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE", "ENGINEERING_TECH", "BIOSYSTEMS_TECH"],
}

# the prior (over-inclusive) state, for a faithful downgrade
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
    print(f"[migration 26] Corrected stream eligibility for {len(_CORRECTIONS)} courses ({total} rows).")


def downgrade() -> None:
    conn = op.get_bind()
    _apply(conn, {code: _ALL_SIX for code in _CORRECTIONS})
