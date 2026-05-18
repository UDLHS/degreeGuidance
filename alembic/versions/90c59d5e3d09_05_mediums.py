"""05 mediums

Revision ID: 90c59d5e3d09
Revises: 7a9673efd038
Create Date: 2026-05-18 15:35:29.919028

"""

from alembic import op
import sqlalchemy as sa

revision = "90c59d5e3d09"
down_revision = "7a9673efd038"
branch_labels = None
depends_on = None


MEDIUMS = [
    ("SI", "Sinhala"),
    ("TA", "Tamil"),
    ("EN", "English"),
]


def upgrade():
    op.create_table(
        "mediums",
        sa.Column("medium_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(10), nullable=False, unique=True),
        sa.Column("name_en", sa.String(50), nullable=False),
    )

    op.bulk_insert(
        sa.table("mediums", sa.column("code", sa.String), sa.column("name_en", sa.String)),
        [{"code": c, "name_en": n} for c, n in MEDIUMS],
    )


def downgrade():
    op.drop_table("mediums")