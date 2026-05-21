"""11 courses name cleanup

Revision ID: 25d1beea7023
Revises: 502c1148b533
Create Date: 2026-05-21 19:01:12.588230

Phase 3.5 cosmetic fix. The Phase 3 courses seed CSV had 19 names with
OCR artifacts that slipped through cleanup:
- "Uni - Code" prefix from table header (courses 012, 039, 075, 112)
- Mis-capitalized parenthesized abbreviations: (sab) (seusl) -ict, etc.

This migration applies the corrections via UPDATE. The Phase 3 seed CSV
has also been re-delivered with the fixes, so fresh setups will not need
this migration (it's a no-op for clean data).
"""

from alembic import op

# KEEP the auto-generated revision and down_revision values above.
revision = "25d1beea7023"
down_revision = "502c1148b533"
branch_labels = None
depends_on = None


def upgrade():
    # Strip "Uni - Code  " (or doubled) prefix
    op.execute(r"""
        UPDATE courses
        SET name_en = regexp_replace(name_en, '^Uni - Code\s+(Uni - Code\s+)?', '')
        WHERE name_en LIKE 'Uni - Code%'
    """)

    # Specific capitalization / spacing fixes
    op.execute("""
        UPDATE courses SET name_en = REPLACE(name_en, 'Arts(sab)', 'Arts (SAB)')
        WHERE name_en LIKE '%Arts(sab)%'
    """)
    op.execute("""
        UPDATE courses
        SET name_en = REPLACE(name_en,
            'Management and Information Technology(seusl)',
            'Management and Information Technology (SEUSL)')
        WHERE name_en LIKE '%Technology(seusl)%'
    """)
    op.execute("""
        UPDATE courses
        SET name_en = REPLACE(name_en, 'Physical Science -ict', 'Physical Science - ICT')
        WHERE name_en LIKE '%Physical Science -ict%'
    """)
    op.execute("""
        UPDATE courses
        SET name_en = REPLACE(name_en,
            'Arts-information Technology', 'Arts - Information Technology')
        WHERE name_en LIKE '%Arts-information%'
    """)
    op.execute("""
        UPDATE courses
        SET name_en = REPLACE(name_en, '(biological Sc.)', '(Biological Sc.)')
        WHERE name_en LIKE '%(biological Sc.)%'
    """)
    op.execute("""
        UPDATE courses
        SET name_en = REPLACE(name_en, '(physical Sc.)', '(Physical Sc.)')
        WHERE name_en LIKE '%(physical Sc.)%'
    """)
    op.execute("""
        UPDATE courses
        SET name_en = REPLACE(name_en,
            'Marine and Freshwater Sciences', 'Marine and Fresh Water Sciences')
        WHERE name_en LIKE '%Freshwater Sciences%'
    """)


def downgrade():
    # No-op: we don't restore typos
    pass