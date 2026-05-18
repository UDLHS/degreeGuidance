"""03 subjects

Revision ID: 30a60cdbaa9e
Revises: 587fcc0e7d44
Create Date: 2026-05-18 15:21:57.421390

"""

from alembic import op
import sqlalchemy as sa

revision = "30a60cdbaa9e"
down_revision = "587fcc0e7d44"
branch_labels = None
depends_on = None


# Core A/L subjects. Practical = subjects with a practical examination component.
# This is a minimal MVP set covering the streams the eligibility engine queries.
# More subjects (Arts baskets, foreign languages) can be added incrementally.
SUBJECTS = [
    # Physical / Bio Science core
    ("COMBINED_MATHEMATICS",       "Combined Mathematics",       False),
    ("HIGHER_MATHEMATICS",         "Higher Mathematics",         False),
    ("MATHEMATICS",                "Mathematics",                False),
    ("PHYSICS",                    "Physics",                    True),
    ("CHEMISTRY",                  "Chemistry",                  True),
    ("BIOLOGY",                    "Biology",                    True),
    ("AGRICULTURAL_SCIENCE",       "Agricultural Science",       True),

    # Commerce
    ("ACCOUNTING",                 "Accounting",                 False),
    ("BUSINESS_STUDIES",           "Business Studies",           False),
    ("ECONOMICS",                  "Economics",                  False),
    ("BUSINESS_STATISTICS",        "Business Statistics",        False),

    # Arts — social sciences basket
    ("HISTORY",                    "History",                    False),
    ("GEOGRAPHY",                  "Geography",                  False),
    ("POLITICAL_SCIENCE",          "Political Science",          False),
    ("LOGIC",                      "Logic & Scientific Method",  False),
    ("HOME_ECONOMICS",             "Home Economics",             False),
    ("COMMUNICATION_STUDIES",      "Communication & Media Studies", False),

    # Arts — languages
    ("SINHALA",                    "Sinhala",                    False),
    ("TAMIL",                      "Tamil",                      False),
    ("ENGLISH",                    "English",                    False),
    ("PALI",                       "Pali",                       False),
    ("SANSKRIT",                   "Sanskrit",                   False),
    ("ARABIC",                     "Arabic",                     False),

    # Arts — religions and civilizations
    ("BUDDHISM",                   "Buddhism",                   False),
    ("HINDUISM",                   "Hinduism",                   False),
    ("CHRISTIANITY",               "Christianity",               False),
    ("ISLAM",                      "Islam",                      False),

    # Arts — aesthetic
    ("ART",                        "Art",                        True),
    ("DANCING",                    "Dancing",                    True),
    ("MUSIC",                      "Music",                      True),
    ("DRAMA_THEATRE",              "Drama & Theatre",            True),

    # Engineering / Biosystems Technology core
    ("ENGINEERING_TECHNOLOGY",     "Engineering Technology",     True),
    ("BIOSYSTEMS_TECHNOLOGY",      "Biosystems Technology",      True),
    ("SCIENCE_FOR_TECHNOLOGY",     "Science for Technology",     True),

    # ICT (cross-stream)
    ("ICT",                        "Information & Communication Technology", True),
]


def upgrade():
    op.create_table(
        "subjects",
        sa.Column("subject_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("name_si", sa.String(150)),
        sa.Column("name_ta", sa.String(150)),
        sa.Column("is_practical", sa.Boolean, nullable=False, server_default=sa.text("false")),
    )

    subjects_table = sa.table(
        "subjects",
        sa.column("code", sa.String),
        sa.column("name_en", sa.String),
        sa.column("is_practical", sa.Boolean),
    )

    op.bulk_insert(
        subjects_table,
        [{"code": code, "name_en": name, "is_practical": prac} for code, name, prac in SUBJECTS],
    )


def downgrade():
    op.drop_table("subjects")