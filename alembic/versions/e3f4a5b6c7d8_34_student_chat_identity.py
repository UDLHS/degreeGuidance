"""34 student chat identity

Adds google_id to users (for OAuth lookup) and student_id to conversations
so a logged-in student's chat sessions can be attributed to them.

Revision ID: e3f4a5b6c7d8
Revises: c1d2e3f4a5b6
Create Date: 2026-06-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'e3f4a5b6c7d8'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('google_id', sa.String(128), nullable=True))
    op.create_index(
        'idx_users_google_id', 'users', ['google_id'], unique=True,
        postgresql_where=sa.text("google_id IS NOT NULL"),
    )

    op.add_column('conversations', sa.Column(
        'student_id',
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey('users.user_id', ondelete='SET NULL'),
        nullable=True,
    ))
    op.execute(
        "CREATE INDEX idx_conversations_student ON conversations "
        "(student_id, updated_at DESC) WHERE student_id IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_conversations_student")
    op.drop_column('conversations', 'student_id')
    op.drop_index('idx_users_google_id', table_name='users')
    op.drop_column('users', 'google_id')
