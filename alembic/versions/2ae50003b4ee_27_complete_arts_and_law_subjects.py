"""27_complete_arts_and_law_subjects

Revision ID: 2ae50003b4ee
Revises: 66e1fd4b50a7
Create Date: 2026-06-22 22:30:54.442013

Found while curating course_requirements: the subjects catalog (35 rows) was
missing real A/L subjects referenced by the Arts basket system (§2.2.1.1) and
Law (§2.2.8.10) -- the 5 Religion/Civilization subjects (distinct from the
religions themselves, e.g. "Buddhist Civilization" vs "Buddhism"), several
foreign languages, and the 6 Technological subjects (Basket 01 item 11).

Adds the 17 missing subjects and links the Arts-relevant ones (all of them
except German, used by Commerce/Facilities Mgmt rather than Arts) to ARTS in
stream_subjects, so the student form's subject picker can offer them.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2ae50003b4ee'
down_revision: Union[str, Sequence[str], None] = '66e1fd4b50a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (code, name_en)
NEW_SUBJECTS = [
    ("BUDDHIST_CIV", "Buddhist Civilization"),
    ("HINDU_CIV", "Hindu Civilization"),
    ("CHRISTIAN_CIV", "Christian Civilization"),
    ("ISLAMIC_CIV", "Islamic Civilization"),
    ("GRECO_ROMAN_CIV", "Greek & Roman Civilization"),
    ("CHINESE", "Chinese"),
    ("FRENCH", "French"),
    ("GERMAN", "German"),
    ("HINDI", "Hindi"),
    ("JAPANESE", "Japanese"),
    ("RUSSIAN", "Russian"),
    ("MALAY", "Malay"),
    ("KOREAN", "Korean"),
    ("CIVIL_TECH", "Civil Technology"),
    ("ELEC_ELECTRONIC_IT_TECH", "Electrical, Electronic and Information Technology"),
    ("AGRO_TECH", "Agro Technology"),
    ("MECHANICAL_TECH", "Mechanical Technology"),
    ("FOOD_TECH", "Food Technology"),
    ("BIO_RESOURCE_TECH", "Bio-Resource Technology"),
]

# Subjects to attach to ARTS in stream_subjects (everything above except
# German, which Commerce/Facilities Mgmt reference but Arts does not).
ARTS_LINK_NAMES = [n for c, n in NEW_SUBJECTS if c != "GERMAN"]


def upgrade() -> None:
    conn = op.get_bind()

    subjects_table = sa.table(
        "subjects",
        sa.column("code", sa.String),
        sa.column("name_en", sa.String),
        sa.column("is_practical", sa.Boolean),
    )
    op.bulk_insert(
        subjects_table,
        [{"code": c, "name_en": n, "is_practical": False} for c, n in NEW_SUBJECTS],
    )

    arts_stream_id = conn.execute(
        sa.text("SELECT stream_id FROM streams WHERE code = 'ARTS'")
    ).scalar_one()
    subject_ids = conn.execute(
        sa.text("SELECT subject_id FROM subjects WHERE name_en = ANY(:names)"),
        {"names": ARTS_LINK_NAMES},
    ).scalars().all()
    if len(subject_ids) != len(ARTS_LINK_NAMES):
        raise RuntimeError(
            f"Expected {len(ARTS_LINK_NAMES)} subjects to link to ARTS, found {len(subject_ids)}."
        )
    for sid in subject_ids:
        conn.execute(
            sa.text(
                "INSERT INTO stream_subjects (stream_id, subject_id) VALUES (:sid, :subid) "
                "ON CONFLICT DO NOTHING"
            ),
            {"sid": arts_stream_id, "subid": sid},
        )
    print(f"[migration 27] Added {len(NEW_SUBJECTS)} subjects, linked {len(subject_ids)} to ARTS.")


def downgrade() -> None:
    conn = op.get_bind()
    codes = [c for c, _ in NEW_SUBJECTS]
    conn.execute(
        sa.text(
            "DELETE FROM stream_subjects WHERE subject_id IN "
            "(SELECT subject_id FROM subjects WHERE code = ANY(:codes))"
        ),
        {"codes": codes},
    )
    conn.execute(sa.text("DELETE FROM subjects WHERE code = ANY(:codes)"), {"codes": codes})
