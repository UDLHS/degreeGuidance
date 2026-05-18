"""06 universities

Revision ID: d803b9eeb74a
Revises: 90c59d5e3d09
Create Date: 2026-05-18 15:36:55.519457

21 state universities and HEIs from the 2024/2025 handbook abbreviation list (page 4).
Each university is associated with its home district (where the main campus sits;
faculties at other locations are modeled separately via the faculties table).
"""

from alembic import op
import sqlalchemy as sa

revision = "d803b9eeb74a"
down_revision = "90c59d5e3d09"
branch_labels = None
depends_on = None


# (code, name_en, short_name, district_code, established)
# Locations verified from handbook "Location -" entries where present;
# remaining locations from established public record.
UNIVERSITIES = [
    ("CMB",     "University of Colombo",                                              "Colombo",      "COLOMBO",      1921),
    ("PDN",     "University of Peradeniya",                                           "Peradeniya",   "KANDY",        1942),
    ("SJP",     "University of Sri Jayewardenepura",                                  "Sri J'pura",   "COLOMBO",      1958),
    ("KLN",     "University of Kelaniya",                                             "Kelaniya",     "GAMPAHA",      1959),
    ("MRT",     "University of Moratuwa",                                             "Moratuwa",     "COLOMBO",      1972),
    ("UJA",     "University of Jaffna",                                               "Jaffna",       "JAFFNA",       1974),
    ("RUH",     "University of Ruhuna",                                               "Ruhuna",       "MATARA",       1978),
    ("EUSL",    "Eastern University, Sri Lanka",                                      "Eastern",      "BATTICALOA",   1981),
    ("SEUSL",   "South Eastern University of Sri Lanka",                              "South East",   "AMPARA",       1995),
    ("RUSL",    "Rajarata University of Sri Lanka",                                   "Rajarata",     "ANURADHAPURA", 1996),
    ("SUSL",    "Sabaragamuwa University of Sri Lanka",                               "Sabaragamuwa", "RATNAPURA",    1995),
    ("WUSL",    "Wayamba University of Sri Lanka",                                    "Wayamba",      "KURUNEGALA",   1999),
    ("UWU",     "Uva Wellassa University of Sri Lanka",                               "Uva Wellassa", "BADULLA",      2005),
    ("UVPA",    "University of the Visual & Performing Arts",                         "UVPA",         "COLOMBO",      2005),
    ("GWUIM",   "Gampaha Wickramarachchi University of Indigenous Medicine",          "GWUIM",        "GAMPAHA",      2021),
    ("UOV",     "University of Vavuniya, Sri Lanka",                                  "Vavuniya",     "VAVUNIYA",     2021),
    ("OUSL",    "The Open University of Sri Lanka",                                   "Open Uni",     "COLOMBO",      1980),
    ("SP",      "Sripalee Campus, University of Colombo",                             "Sripalee",     "KALUTARA",     1996),
    ("TRINCO",  "Trincomalee Campus, Eastern University, Sri Lanka",                  "Trinco",       "TRINCOMALEE",  1986),
    ("UCSC",    "University of Colombo School of Computing",                          "UCSC",         "COLOMBO",      2002),
    ("SVIAS",   "Swamy Vipulananda Institute of Aesthetic Studies, Eastern University", "SVIAS",      "BATTICALOA",   1981),
]


def upgrade():
    op.create_table(
        "universities",
        sa.Column("university_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name_en", sa.String(150), nullable=False),
        sa.Column("name_si", sa.String(200)),
        sa.Column("name_ta", sa.String(200)),
        sa.Column("short_name", sa.String(50)),
        sa.Column(
            "district_id",
            sa.Integer,
            sa.ForeignKey("districts.district_id", ondelete="SET NULL"),
        ),
        sa.Column("website_url", sa.Text),
        sa.Column("established", sa.Integer),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
    )

    # Resolve district codes to IDs
    conn = op.get_bind()
    district_rows = conn.execute(sa.text("SELECT district_id, code FROM districts")).fetchall()
    district_ids = {row.code: row.district_id for row in district_rows}

    rows = []
    for code, name_en, short, district_code, established in UNIVERSITIES:
        did = district_ids.get(district_code)
        if did is None:
            raise RuntimeError(f"District not found for {code}: {district_code}")
        rows.append({
            "code": code,
            "name_en": name_en,
            "short_name": short,
            "district_id": did,
            "established": established,
            "is_active": True,
        })

    op.bulk_insert(
        sa.table(
            "universities",
            sa.column("code", sa.String),
            sa.column("name_en", sa.String),
            sa.column("short_name", sa.String),
            sa.column("district_id", sa.Integer),
            sa.column("established", sa.Integer),
            sa.column("is_active", sa.Boolean),
        ),
        rows,
    )


def downgrade():
    op.drop_table("universities")