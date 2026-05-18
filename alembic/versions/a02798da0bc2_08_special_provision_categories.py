"""08 special provision categories

Revision ID: a02798da0bc2
Revises: 87e1c889ddde
Create Date: 2026-05-18 15:40:42.935995

"""

from alembic import op
import sqlalchemy as sa

revision = "a02798da0bc2"
down_revision = "87e1c889ddde"
branch_labels = None
depends_on = None


# Handbook Section 6 — 6 special admission categories.
CATEGORIES = [
    ("BLIND",           "Blind and Differently Abled Candidates",
     "Candidates with blindness or other disabilities admitted under special provisions.",
     "6.1"),
    ("EXTRACURRICULAR", "Extracurricular Activities Excellence",
     "Students who have excelled in extracurricular activities at national/international level.",
     "6.2"),
    ("SPORTS",          "Exceptional Sports Abilities",
     "Candidates with exceptional abilities or skills in sports.",
     "6.3"),
    ("MILITARY",        "Armed Forces and Police",
     "Enlisted personnel of armed forces, police service and special task force.",
     "6.4"),
    ("FOREIGN",         "Foreign / Sri Lankans Studied Abroad",
     "Sri Lankans who studied abroad and foreign students.",
     "6.5"),
    ("TEACHER",         "Teachers",
     "Admission of qualified teachers under the teacher quota.",
     "6.6"),
]


def upgrade():
    op.create_table(
        "special_provision_categories",
        sa.Column("category_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("handbook_section", sa.String(20)),
    )

    op.bulk_insert(
        sa.table(
            "special_provision_categories",
            sa.column("code", sa.String),
            sa.column("name_en", sa.String),
            sa.column("description", sa.Text),
            sa.column("handbook_section", sa.String),
        ),
        [
            {"code": c, "name_en": n, "description": d, "handbook_section": s}
            for c, n, d, s in CATEGORIES
        ],
    )


def downgrade():
    op.drop_table("special_provision_categories")