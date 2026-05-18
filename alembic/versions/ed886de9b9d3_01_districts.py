"""01 districts

Revision ID: (auto-filled by alembic)
Revises: (auto-filled by alembic)
Create Date: (auto-filled by alembic)

Seeds the 25 Sri Lankan administrative districts with the 16 educationally
disadvantaged districts flagged (handbook Section 1.1).
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic — DO NOT EDIT
revision = 'ed886de9b9d3'  # alembic auto-fills this
down_revision = None  # alembic auto-fills this
branch_labels = None
depends_on = None


# 16 disadvantaged districts per handbook Section 1.1
DISADVANTAGED = {
    "NUWARA_ELIYA", "HAMBANTOTA", "JAFFNA", "KILINOCHCHI",
    "MANNAR", "MULLAITIVU", "VAVUNIYA", "TRINCOMALEE",
    "BATTICALOA", "AMPARA", "PUTTALAM", "ANURADHAPURA",
    "POLONNARUWA", "BADULLA", "MONARAGALA", "RATNAPURA",
}

# 25 districts: (code, name_en, province)
DISTRICTS = [
    ("COLOMBO",       "Colombo",       "Western"),
    ("GAMPAHA",       "Gampaha",       "Western"),
    ("KALUTARA",      "Kalutara",      "Western"),
    ("KANDY",         "Kandy",         "Central"),
    ("MATALE",        "Matale",        "Central"),
    ("NUWARA_ELIYA",  "Nuwara Eliya",  "Central"),
    ("GALLE",         "Galle",         "Southern"),
    ("MATARA",        "Matara",        "Southern"),
    ("HAMBANTOTA",    "Hambantota",    "Southern"),
    ("JAFFNA",        "Jaffna",        "Northern"),
    ("KILINOCHCHI",   "Kilinochchi",   "Northern"),
    ("MANNAR",        "Mannar",        "Northern"),
    ("VAVUNIYA",      "Vavuniya",      "Northern"),
    ("MULLAITIVU",    "Mullaitivu",    "Northern"),
    ("BATTICALOA",    "Batticaloa",    "Eastern"),
    ("AMPARA",        "Ampara",        "Eastern"),
    ("TRINCOMALEE",   "Trincomalee",   "Eastern"),
    ("KURUNEGALA",    "Kurunegala",    "North Western"),
    ("PUTTALAM",      "Puttalam",      "North Western"),
    ("ANURADHAPURA",  "Anuradhapura",  "North Central"),
    ("POLONNARUWA",   "Polonnaruwa",   "North Central"),
    ("BADULLA",       "Badulla",       "Uva"),
    ("MONARAGALA",    "Monaragala",    "Uva"),
    ("RATNAPURA",     "Ratnapura",     "Sabaragamuwa"),
    ("KEGALLE",       "Kegalle",       "Sabaragamuwa"),
]


def upgrade():
    op.create_table(
        "districts",
        sa.Column("district_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name_en", sa.String(50), nullable=False),
        sa.Column("name_si", sa.String(100)),
        sa.Column("name_ta", sa.String(100)),
        sa.Column("province", sa.String(50)),
        sa.Column("is_disadvantaged", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    districts_table = sa.table(
        "districts",
        sa.column("code", sa.String),
        sa.column("name_en", sa.String),
        sa.column("province", sa.String),
        sa.column("is_disadvantaged", sa.Boolean),
    )

    op.bulk_insert(
        districts_table,
        [
            {
                "code": code,
                "name_en": name_en,
                "province": province,
                "is_disadvantaged": code in DISADVANTAGED,
            }
            for code, name_en, province in DISTRICTS
        ],
    )


def downgrade():
    op.drop_table("districts")