"""20 auth events

Admin Slice 1, Part A2 (masterplan §15.2). Append-only authentication audit
trail. The login route writes one row per attempt (success or failure); a
failed login with an unknown email records with user_id NULL.

The masterplan mentions auth_events (§15.2) but gives no DDL, so this schema is
designed here: nullable user_id (ON DELETE SET NULL so history survives user
deletion), an event_type CHECK, and DESC indexes for "recent events" lookups.

Revision ID: <FILL_FROM_GENERATED_STUB>
Revises: <FILL_FROM_GENERATED_STUB>   # migration 19 hash (current head)
Create Date: <FILL_FROM_GENERATED_STUB>
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers.
revision = '2ccafb3d723e'
down_revision = '70cacf08afcc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_events",
        sa.Column("event_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("email", sa.String(255)),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("ip_hash", sa.String(64)),
        sa.Column("user_agent", sa.Text),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "event_type IN ('login_success', 'login_failure', 'logout', 'token_refresh')",
            name="ck_auth_events_type",
        ),
    )
    op.execute("CREATE INDEX idx_auth_events_user ON auth_events (user_id, created_at DESC)")
    op.execute("CREATE INDEX idx_auth_events_email ON auth_events (email, created_at DESC)")


def downgrade() -> None:
    op.drop_table("auth_events")  # indexes drop with the table
