"""add 5 missing courses from 2024 handbook

Revision ID: 65a2d08989b1
Revises: 5fcd67dbeceb
Create Date: 2026-05-24 18:39:01.945754

--- Add 5 courses missing from Section 5 but present in cutoff tables (Sec 9). ---

Discovered during Phase 5 (cutoff ingestion) when the native extractor flagged
5 Uni-Codes as "NOT IN SEED":
  006K, 040R, 040W, 042L, 271D

These are real courses that appear in the 2024 handbook cutoff tables but are
NOT listed in Section 5's Course of Study index. Verified by:
  1. Cross-referencing the 90°-rotated code column with the 180°-rotated label
     column on cutoff pages 180, 182, 183
  2. Confirming the labels match standard UGC course/university names

--- Post-application correction (Cleanup #2 from handoff) ---

The original version of this file used the stream code abbreviation for 040R/040W
eligibility that does NOT exist in streams.code (the real value is the full
spelled-out one). Because the original INSERT was an INSERT...SELECT, the
mismatch silently inserted zero rows instead of raising; the partial state was
hand-patched in the DB at the time. This file is now corrected so a fresh
`alembic upgrade head` reproduces the same 15 eligibility rows as the live DB,
and a pre-validation block was added to upgrade() so this silent-failure mode
cannot recur for any future stream/university code typo in this migration.
"""
from alembic import op
import sqlalchemy as sa

revision = '65a2d08989b1'
down_revision = '5fcd67dbeceb'
branch_labels = None
depends_on = None


# (course_code, course_number, university_code, name_en, requires_aptitude_test)
NEW_COURSES = [
    ('006K', '006', 'RUSL',
     'Applied Sciences (Bio.Sc) (Rajarata University of Sri Lanka)',
     False),
    ('040R', '040', 'UOV',
     'Management Studies (TV) - B (University of Vavuniya, Sri Lanka)',
     False),
    ('040W', '040', 'TRINCO',
     'Management Studies (TV) - B (Trincomalee Campus, Eastern University, Sri Lanka)',
     False),
    ('042L', '042', 'SUSL',
     'Arts (SAB) - B (Sabaragamuwa University of Sri Lanka)',
     False),
    ('271D', '271', 'KLN',
     'Management and Information Technology (MIT) (Bio Science Stream) (University of Kelaniya)',
     False),
]

# (course_code, alias_text)
NEW_ALIASES = [
    ('006K', 'APPLIED SCIENCES (BIO.SC) (RAJARATA UNIVERSITY OF SRI LANKA)'),
    ('040R', 'MANAGEMENT STUDIES (TV) - B (UNIVERSITY OF VAVUNIYA, SRI LANKA)'),
    ('040W', 'MANAGEMENT STUDIES (TV) - B (TRINCOMALEE CAMPUS, EASTERN UNIVERSITY, SRI LANKA)'),
    ('042L', 'ARTS (SAB) - B (SABARAGAMUWA UNIVERSITY OF SRI LANKA)'),
    ('271D', 'MANAGEMENT AND INFORMATION TECHNOLOGY (MIT) (BIO SCIENCE STREAM) (UNIVERSITY OF KELANIYA)'),
]

# (course_code, stream_code)
# NOTE: stream_code values must match streams.code exactly. The "all 6 streams"
# expansion for 040R/040W excludes ICT, matching the cross-stream convention in
# migration 12 (handbook §2.2.7/§2.2.8).
NEW_ELIGIBILITY = [
    ('006K', 'BIO_SCIENCE'),
    # 040R / 040W: [Any subject combination] → eligible for all 6 streams
    ('040R', 'ARTS'),
    ('040R', 'COMMERCE'),
    ('040R', 'BIO_SCIENCE'),
    ('040R', 'PHYSICAL_SCIENCE'),
    ('040R', 'ENGINEERING_TECH'),
    ('040R', 'BIOSYSTEMS_TECH'),
    ('040W', 'ARTS'),
    ('040W', 'COMMERCE'),
    ('040W', 'BIO_SCIENCE'),
    ('040W', 'PHYSICAL_SCIENCE'),
    ('040W', 'ENGINEERING_TECH'),
    ('040W', 'BIOSYSTEMS_TECH'),
    ('042L', 'COMMERCE'),         # [Commerce Stream]
    ('271D', 'BIO_SCIENCE'),      # (Bio Science Stream)
]


def upgrade() -> None:
    conn = op.get_bind()

    # --- Pre-validate FK references to prevent silent INSERT...SELECT no-ops ---
    # An INSERT...SELECT against a missing reference inserts zero rows without
    # raising. Validating here turns a stream/university code typo into a loud
    # failure instead of a partially-applied migration.
    valid_uni_codes = {
        row.code for row in conn.execute(
            sa.text("SELECT code FROM universities")
        ).fetchall()
    }
    for code, _, uni_code, _, _ in NEW_COURSES:
        if uni_code not in valid_uni_codes:
            raise RuntimeError(
                f"University code {uni_code!r} not found "
                f"(needed for course {code!r}). Migration 06 must run first."
            )

    valid_stream_codes = {
        row.code for row in conn.execute(
            sa.text("SELECT code FROM streams")
        ).fetchall()
    }
    for code, stream_code in NEW_ELIGIBILITY:
        if stream_code not in valid_stream_codes:
            raise RuntimeError(
                f"Stream code {stream_code!r} not found "
                f"(needed for course {code!r}). Migration 02 must run first."
            )

    # 1) Insert courses (look up university_id from universities.code)
    for code, num, uni_code, name, apt in NEW_COURSES:
        # Escape single quotes in name (none in our data, but defensive)
        name_sql = name.replace("'", "''")
        op.execute(f"""
            INSERT INTO courses
                (course_code, course_number, university_id, name_en,
                 selection_basis, requires_aptitude_test)
            SELECT
                '{code}', '{num}', u.university_id, '{name_sql}',
                'district_quota', {str(apt).upper()}
            FROM universities u
            WHERE u.code = '{uni_code}'
        """)

    # 2) Insert aliases (direct, course_code is the FK)
    for code, alias in NEW_ALIASES:
        alias_sql = alias.replace("'", "''")
        op.execute(f"""
            INSERT INTO course_aliases (course_code, alias_text, source, is_verified)
            VALUES ('{code}', '{alias_sql}', 'manual_seed_2024_handbook_fix', TRUE)
        """)

    # 3) Insert stream eligibility (look up stream_id from streams.code)
    for code, stream_code in NEW_ELIGIBILITY:
        op.execute(f"""
            INSERT INTO course_stream_eligibility (course_code, stream_id)
            SELECT '{code}', s.stream_id
            FROM streams s
            WHERE s.code = '{stream_code}'
        """)


def downgrade() -> None:
    codes_in = "('006K','040R','040W','042L','271D')"
    # Cascading FK on course_aliases and course_stream_eligibility means deleting
    # courses would auto-cascade, but be explicit for safety:
    op.execute(f"DELETE FROM course_stream_eligibility WHERE course_code IN {codes_in}")
    op.execute(f"DELETE FROM course_aliases WHERE course_code IN {codes_in}")
    op.execute(f"DELETE FROM courses WHERE course_code IN {codes_in}")
