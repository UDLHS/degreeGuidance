"""17 unicode self aliases

Adds one alias per course where alias_text = course_code (e.g., '001A' is
an alias for course '001A'). This is required so the ingestion script
(apps/worker/jobs/ingest_zscores.py) can resolve CSV column headers that
are bare Uni-Codes (as produced by the native_pdf_extractor v7) -- without
this, the script's alias lookup fails because the original aliases are
full label strings like 'MEDICINE (University of Colombo)'.

These self-aliases were originally inserted via raw SQL during Phase 5 in
the previous chat session, tagged with source = 'unicode_self_alias_2024'.
This migration formalizes them so that rebuilding the DB from migrations
produces a state consistent with the live DB.

CORRECTION (from the audit): the source string MUST be 'unicode_self_alias_2024'
to match the rows already present in the live DB. The earlier draft used the
bare 'unicode_self_alias', which would (a) make downgrade() match zero live
rows, and (b) make a fresh rebuild tag rows differently than the live DB.

This migration depends on migration 16 (the courses-fix that adds 006K, 040R,
040W, 042L, 271D), so down_revision is migration 16's hash. Because it uses
ON CONFLICT (alias_text, course_code) DO NOTHING, applying it to the live DB
(where all 266 rows already exist) is a clean no-op; on a fresh rebuild it
inserts all 266.

Revision ID: <FILL_FROM_GENERATED_STUB>
Revises: 65a2d08989b1
Create Date: <FILL_FROM_GENERATED_STUB>
"""
from alembic import op


# revision identifiers.
# IMPORTANT: replace ONLY the revision value below with the hash alembic
# generated in the stub filename. Leave down_revision as the migration-16 hash.
revision = 'f7a8b457dce3'
down_revision = '65a2d08989b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Insert one self-alias per course. Idempotent via ON CONFLICT DO NOTHING."""
    op.execute("""
        INSERT INTO course_aliases (course_code, alias_text, source, is_verified)
        SELECT course_code,
               course_code,
               'unicode_self_alias_2024',
               TRUE
        FROM courses
        ON CONFLICT (alias_text, course_code) DO NOTHING
    """)


def downgrade() -> None:
    """Remove only the self-aliases (where alias_text matches course_code)."""
    op.execute("""
        DELETE FROM course_aliases
        WHERE source = 'unicode_self_alias_2024'
          AND alias_text = course_code
    """)
