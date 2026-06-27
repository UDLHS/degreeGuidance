"""33_career_industry_tags

Add career_tags text[] and industry_tags text[] to the courses table.
These activate the dormant career (weight=0.25) and industry (weight=0.15)
scoring dimensions without any schema incompatibility — existing rows just
get empty arrays until the populate_career_tags script fills them.

Revision ID: c1d2e3f4a5b6
Revises: b2c3d4e5f6a7
Create Date: 2026-06-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "courses",
        sa.Column(
            "career_tags",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "courses",
        sa.Column(
            "industry_tags",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )
    op.execute(
        "CREATE INDEX idx_courses_career_tags ON courses USING gin(career_tags)"
    )
    op.execute(
        "CREATE INDEX idx_courses_industry_tags ON courses USING gin(industry_tags)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_courses_industry_tags")
    op.execute("DROP INDEX IF EXISTS idx_courses_career_tags")
    op.drop_column("courses", "industry_tags")
    op.drop_column("courses", "career_tags")
