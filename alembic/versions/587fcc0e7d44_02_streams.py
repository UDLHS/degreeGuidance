"""02 streams"""

from alembic import op
import sqlalchemy as sa

revision = '587fcc0e7d44'
down_revision = 'ed886de9b9d3'
branch_labels = None
depends_on = None


STREAMS = [
    ("ARTS",              "Arts",                                  None),
    ("COMMERCE",          "Commerce",                              None),
    ("BIO_SCIENCE",       "Biological Science",                    None),
    ("PHYSICAL_SCIENCE",  "Physical Science",                      None),
    ("ENGINEERING_TECH",  "Engineering Technology",                None),
    ("BIOSYSTEMS_TECH",   "Biosystems Technology",                 None),
    ("ICT",               "Information Communication Technology",
     "Navigation category for courses accepting ICT/SFT/ET/BST subjects "
     "(handbook Section 2.2.7). Not a standalone A/L stream."),
]


def upgrade():
    op.create_table(
        "streams",
        sa.Column("stream_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("name_en", sa.String(50), nullable=False),
        sa.Column("name_si", sa.String(100)),
        sa.Column("name_ta", sa.String(100)),
        sa.Column("description", sa.Text),
    )

    streams_table = sa.table(
        "streams",
        sa.column("code", sa.String),
        sa.column("name_en", sa.String),
        sa.column("description", sa.Text),
    )

    op.bulk_insert(
        streams_table,
        [{"code": code, "name_en": name_en, "description": desc} for code, name_en, desc in STREAMS],
    )


def downgrade():
    op.drop_table("streams")