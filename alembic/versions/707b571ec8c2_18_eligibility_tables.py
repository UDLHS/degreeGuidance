"""18 eligibility tables

Phase 6. Creates the two tables the eligibility engine needs:

  1. course_mediums      — junction courses <-> mediums (mirrors
                           course_stream_eligibility). Empty until Phase 9
                           admin work populates it; the engine returns
                           available_mediums = [] until then.

  2. eligibility_audit   — one row per eligibility query, for forensic
                           investigation (masterplan v4 §5.1 item 4).

DEFERRED FK (important): the masterplan spec for eligibility_audit.user_id is
`UUID REFERENCES users(user_id) ON DELETE SET NULL`. The users table does not
exist until Phase 8, so user_id is created here as a plain nullable UUID with
NO foreign key. The FK constraint is added by the Phase 8 migration that
creates users. In Phase 6 (no auth) user_id is always NULL.

Revision ID: <FILL_FROM_GENERATED_STUB>
Revises: <FILL_FROM_GENERATED_STUB>   # the migration 17 hash (current head)
Create Date: <FILL_FROM_GENERATED_STUB>
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers.
# Replace ONLY `revision` with the hash alembic generated in the stub filename.
# Leave `down_revision` as the value alembic auto-filled (your migration 17 hash).
revision = '707b571ec8c2'
down_revision = 'f7a8b457dce3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) course_mediums — courses <-> mediums junction
    op.create_table(
        "course_mediums",
        sa.Column(
            "course_code",
            sa.String(15),
            sa.ForeignKey("courses.course_code", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "medium_id",
            sa.Integer,
            sa.ForeignKey("mediums.medium_id"),
            primary_key=True,
        ),
    )

    # 2) eligibility_audit — one row per eligibility query
    op.create_table(
        "eligibility_audit",
        sa.Column("audit_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("request_hash", sa.String(64), nullable=False),
        # FK to users(user_id) deferred to Phase 8 (users table doesn't exist yet).
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("z_score", sa.Numeric(6, 4), nullable=False),
        sa.Column(
            "district_id",
            sa.Integer,
            sa.ForeignKey("districts.district_id"),
            nullable=False,
        ),
        sa.Column(
            "stream_id",
            sa.Integer,
            sa.ForeignKey("streams.stream_id"),
            nullable=False,
        ),
        sa.Column("cutoff_year_used", sa.Integer, nullable=False),
        sa.Column("eligible_count", sa.Integer, nullable=False),
        sa.Column("conditional_count", sa.Integer, nullable=False),
        sa.Column("confidence_tier", sa.String(20), nullable=False),
        sa.Column("result_payload", postgresql.JSONB, nullable=False),
        sa.Column("latency_ms", sa.Integer),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Indexes (raw SQL to express the DESC ordering exactly as the spec).
    op.execute(
        "CREATE INDEX idx_eligibility_audit_user "
        "ON eligibility_audit (user_id, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX idx_eligibility_audit_hash "
        "ON eligibility_audit (request_hash)"
    )


def downgrade() -> None:
    # Indexes drop automatically with the table.
    op.drop_table("eligibility_audit")
    op.drop_table("course_mediums")
