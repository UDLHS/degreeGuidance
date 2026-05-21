"""10 course markers

Revision ID: 502c1148b533
Revises: 49cd0ba8b89d
Create Date: 2026-05-20 22:38:11.964566

Applies the * (all-island merit) and # (aptitude test) markers from
handbook §1.1 and §9 page 152. OCR doesn't capture these markers; this
migration encodes them by course_number.

Verification sources:
- All-island merit list: handbook §1.1 (the 6 aesthetic exceptions
  rule applies to §2.2.1 items 1-11 and §2.2.1.2, §2.2.1.3).
- Aptitude test list: handbook page 152, "REQUIREMENT TO PASS THE
  PRACTICAL/APTITUDE TEST" section.

The schema allows both flags to be set independently:
- 020 (Arts SP - Mass Media) and 041 (Arts SP - Performing Arts) are
  BOTH all-island merit AND require aptitude test.
"""

from alembic import op


revision = "502c1148b533"
down_revision = "49cd0ba8b89d"
branch_labels = None
depends_on = None


# 11 course_numbers — all-island merit (Arts stream courses except the
# 6 aesthetic-arts exceptions). Verified from handbook §2.2.1 listing
# items 1-11 (minus aesthetic ones at UVPA/UJA/SVIAS) and §2.2.1.2/.3.
ALL_ISLAND_MERIT_COURSE_NUMBERS = [
    "019",  # Arts
    "020",  # Arts (SP) - Mass Media
    "021",  # Arts (SAB)
    "029",  # Communication Studies
    "031",  # Peace and Conflict Resolution
    "041",  # Arts (SP) - Performing Arts
    "063",  # Islamic Studies
    "084",  # Arabic Language
    "105",  # Teaching English as a Second Language (TESL)
    "112",  # Social Work
    "128",  # Arts-Information Technology
]


# 15 course_numbers — aptitude test required. Verified from handbook
# page 152 "REQUIREMENT TO PASS THE PRACTICAL/APTITUDE TEST" listing
# all aptitude-test Uni-Codes; these are the distinct course_numbers.
APTITUDE_TEST_COURSE_NUMBERS = [
    "020",  # Arts (SP) - Mass Media
    "023",  # Architecture
    "024",  # Design
    "034",  # Fashion Design & Product Development
    "041",  # Arts (SP) - Performing Arts
    "068",  # Music
    "069",  # Dance
    "070",  # Art & Design
    "071",  # Drama & Theatre
    "072",  # Visual & Technological Arts
    "081",  # Physical Education
    "082",  # Sports Science & Management
    "085",  # Visual Arts
    "097",  # Landscape Architecture
    "100",  # Film & Television Studies
]


def upgrade():
    # Apply all-island merit flag
    all_island_csv = ",".join(f"'{n}'" for n in ALL_ISLAND_MERIT_COURSE_NUMBERS)
    op.execute(f"""
        UPDATE courses
        SET selection_basis = 'all_island_merit'
        WHERE course_number IN ({all_island_csv})
    """)

    # Apply aptitude test flag
    apt_csv = ",".join(f"'{n}'" for n in APTITUDE_TEST_COURSE_NUMBERS)
    op.execute(f"""
        UPDATE courses
        SET requires_aptitude_test = TRUE
        WHERE course_number IN ({apt_csv})
    """)


def downgrade():
    # Revert both flags to defaults
    op.execute("UPDATE courses SET selection_basis = 'district_quota'")
    op.execute("UPDATE courses SET requires_aptitude_test = FALSE")