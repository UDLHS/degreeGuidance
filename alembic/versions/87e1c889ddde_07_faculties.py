"""07 faculties

Revision ID: 87e1c889ddde
Revises: d803b9eeb74a
Create Date: 2026-05-18 15:38:13.976648

Empty initially. Populated incrementally as factsheets are written and
faculty info is gathered. Admin UI (Slice 2, Week 5) will manage these
through the web interface.
"""

from alembic import op
import sqlalchemy as sa

revision = "87e1c889ddde"
down_revision = "d803b9eeb74a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "faculties",
        sa.Column("faculty_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "university_id",
            sa.Integer,
            sa.ForeignKey("universities.university_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name_en", sa.String(200), nullable=False),
        sa.Column("short_name", sa.String(50)),
        sa.Column("website_url", sa.Text),
        sa.UniqueConstraint("university_id", "name_en", name="uq_faculty_per_university"),
    )


def downgrade():
    op.drop_table("faculties")