"""19 auth foundation

Admin Slice 1, Part A1 (masterplan v4 §14.5, §5.1 items 5-6, §14.2).

Creates the identity + admin-audit foundation that every admin feature depends on:

  1. users          -- minimal admin-sufficient identity table WITH the role
                       column (student | admin | superadmin). Week 5 EXTENDS this
                       (student_profiles etc.); it is NOT recreated there.
  2. admin_actions   -- append-only audit trail of every admin mutation
                       (exact DDL from masterplan §5.1 item 6).

It also closes the FK deferred in Phase 6 (migration 18): eligibility_audit.user_id
now references users(user_id) ON DELETE SET NULL. Existing audit rows all have
user_id = NULL (no auth in Phase 6), so the constraint applies cleanly.

NOTE on the masterplan inconsistency: §17 Week 2 says create users here (Week 2,
for admin login); §5.1/§17 Week 5 imply users is created in Week 5. Admin login
cannot work without users, so it is created here and merely extended in Week 5.

Revision ID: <FILL_FROM_GENERATED_STUB>
Revises: <FILL_FROM_GENERATED_STUB>   # migration 18 hash (current head)
Create Date: <FILL_FROM_GENERATED_STUB>
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers.
# Replace ONLY `revision` with the generated hash; leave `down_revision` as the
# value alembic auto-filled (your migration 18 hash).
revision = '70cacf08afcc'
down_revision = '707b571ec8c2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) users -------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("display_name", sa.String(150)),
        sa.Column("password_hash", sa.String(255)),  # credentials auth; NULL for OAuth-only
        sa.Column("role", sa.String(20), nullable=False, server_default="student"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "role IN ('student', 'admin', 'superadmin')", name="ck_users_role"
        ),
    )
    # partial index: only non-student roles matter for admin lookups
    op.create_index(
        "idx_users_role", "users", ["role"], postgresql_where=sa.text("role != 'student'")
    )

    # 2) admin_actions (exact §5.1 item 6 DDL) ----------------------------
    op.create_table(
        "admin_actions",
        sa.Column("action_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "admin_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("target_table", sa.String(50)),
        sa.Column("target_id", sa.String(100)),
        sa.Column("before_value", postgresql.JSONB),
        sa.Column("after_value", postgresql.JSONB),
        sa.Column("notes", sa.Text),
        sa.Column("ip_hash", sa.String(64)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    # DESC indexes via raw SQL to match the spec exactly
    op.execute(
        "CREATE INDEX idx_admin_actions_admin "
        "ON admin_actions (admin_user_id, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX idx_admin_actions_target "
        "ON admin_actions (target_table, target_id)"
    )
    op.execute(
        "CREATE INDEX idx_admin_actions_type "
        "ON admin_actions (action_type, created_at DESC)"
    )

    # 3) close the FK deferred in Phase 6 ---------------------------------
    op.create_foreign_key(
        "eligibility_audit_user_id_fkey",
        "eligibility_audit",
        "users",
        ["user_id"],
        ["user_id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "eligibility_audit_user_id_fkey", "eligibility_audit", type_="foreignkey"
    )
    op.drop_table("admin_actions")  # its indexes drop with the table
    op.drop_index("idx_users_role", table_name="users")
    op.drop_table("users")
