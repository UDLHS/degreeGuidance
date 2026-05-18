"""04 stream_subjects

Revision ID: 7a9673efd038
Revises: 30a60cdbaa9e
Create Date: 2026-05-18 15:23:31.304406

"""

from alembic import op
import sqlalchemy as sa

revision = "7a9673efd038"
down_revision = "30a60cdbaa9e"
branch_labels = None
depends_on = None


# stream code -> list of subject codes that count toward that stream.
# For MVP: covers core subjects per stream. Arts has many more "basket" subjects;
# those can be added incrementally without changing this migration.
STREAM_SUBJECTS = {
    "PHYSICAL_SCIENCE": [
        "COMBINED_MATHEMATICS", "HIGHER_MATHEMATICS", "MATHEMATICS",
        "PHYSICS", "CHEMISTRY", "ICT",
    ],
    "BIO_SCIENCE": [
        "BIOLOGY", "CHEMISTRY", "PHYSICS", "AGRICULTURAL_SCIENCE",
    ],
    "COMMERCE": [
        "ACCOUNTING", "BUSINESS_STUDIES", "ECONOMICS", "BUSINESS_STATISTICS",
        "ICT",
    ],
    "ARTS": [
        "HISTORY", "GEOGRAPHY", "POLITICAL_SCIENCE", "LOGIC", "HOME_ECONOMICS",
        "COMMUNICATION_STUDIES", "ECONOMICS",
        "SINHALA", "TAMIL", "ENGLISH", "PALI", "SANSKRIT", "ARABIC",
        "BUDDHISM", "HINDUISM", "CHRISTIANITY", "ISLAM",
        "ART", "DANCING", "MUSIC", "DRAMA_THEATRE",
        "ICT", "AGRICULTURAL_SCIENCE",
    ],
    "ENGINEERING_TECH": [
        "ENGINEERING_TECHNOLOGY", "SCIENCE_FOR_TECHNOLOGY",
        "ICT", "AGRICULTURAL_SCIENCE",
    ],
    "BIOSYSTEMS_TECH": [
        "BIOSYSTEMS_TECHNOLOGY", "SCIENCE_FOR_TECHNOLOGY",
        "ICT", "AGRICULTURAL_SCIENCE",
    ],
    "ICT": [  # Navigation category — subjects from ENG_TECH / BIOSYSTEMS_TECH / SFT
        "ICT", "ENGINEERING_TECHNOLOGY", "BIOSYSTEMS_TECHNOLOGY",
        "SCIENCE_FOR_TECHNOLOGY",
    ],
}


def upgrade():
    op.create_table(
        "stream_subjects",
        sa.Column(
            "stream_id",
            sa.Integer,
            sa.ForeignKey("streams.stream_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "subject_id",
            sa.Integer,
            sa.ForeignKey("subjects.subject_id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # Resolve codes to IDs using the active connection
    conn = op.get_bind()
    stream_rows = conn.execute(sa.text("SELECT stream_id, code FROM streams")).fetchall()
    subject_rows = conn.execute(sa.text("SELECT subject_id, code FROM subjects")).fetchall()
    stream_ids = {row.code: row.stream_id for row in stream_rows}
    subject_ids = {row.code: row.subject_id for row in subject_rows}

    rows = []
    for stream_code, subject_codes in STREAM_SUBJECTS.items():
        sid = stream_ids.get(stream_code)
        if sid is None:
            raise RuntimeError(f"Stream not found: {stream_code}")
        for subject_code in subject_codes:
            subid = subject_ids.get(subject_code)
            if subid is None:
                raise RuntimeError(f"Subject not found: {subject_code}")
            rows.append({"stream_id": sid, "subject_id": subid})

    op.bulk_insert(
        sa.table(
            "stream_subjects",
            sa.column("stream_id", sa.Integer),
            sa.column("subject_id", sa.Integer),
        ),
        rows,
    )


def downgrade():
    op.drop_table("stream_subjects")