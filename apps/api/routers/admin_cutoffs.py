"""Admin cutoff viewer — read-only browse of z_score_cutoffs.

GET /api/admin/cutoffs/years            -> available exam years + counts
GET /api/admin/cutoffs/matrix?year=&q=  -> a whole year as course x district
GET /api/admin/cutoffs/export?year=     -> that year's matrix as a CSV download

6k+ cutoffs are unusable one row at a time, so the matrix returns an entire
year at once (course rows x district columns) for the UI to render as one
scrollable, searchable grid, plus a CSV export for offline checking. Read-only
and admin-gated; touches nothing.
"""

from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_current_admin, get_db

router = APIRouter(
    prefix="/api/admin/cutoffs",
    tags=["admin:cutoffs"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/years")
async def list_years(db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = (
        await db.execute(
            text(
                "SELECT year, count(DISTINCT course_code) AS courses, "
                "count(*) AS cells, count(z_score) AS with_values "
                "FROM z_score_cutoffs GROUP BY year ORDER BY year DESC"
            )
        )
    ).mappings().all()
    return [dict(r) for r in rows]


async def _districts(db: AsyncSession) -> list[dict]:
    rows = (
        await db.execute(
            text("SELECT district_id, code, name_en FROM districts ORDER BY district_id")
        )
    ).mappings().all()
    return [dict(r) for r in rows]


async def _matrix(db: AsyncSession, year: int, q: str | None) -> dict:
    districts = await _districts(db)
    params: dict = {"y": year}
    where = "z.year = :y"
    if q and q.strip():
        where += " AND (c.course_code ILIKE :q OR c.name_en ILIKE :q OR u.code ILIKE :q)"
        params["q"] = f"%{q.strip()}%"

    rows = (
        await db.execute(
            text(
                "SELECT z.course_code, z.district_id, z.z_score, z.notes, "
                "c.name_en, c.course_number, c.is_active, u.code AS university_code "
                "FROM z_score_cutoffs z "
                "JOIN courses c ON c.course_code = z.course_code "
                "LEFT JOIN universities u ON u.university_id = c.university_id "
                f"WHERE {where} ORDER BY z.course_code"
            ),
            params,
        )
    ).mappings().all()

    by_course: dict[str, dict] = {}
    for r in rows:
        course = by_course.setdefault(
            r["course_code"],
            {
                "course_code": r["course_code"],
                "course_number": r["course_number"],
                "name_en": r["name_en"],
                "university_code": r["university_code"],
                "is_active": r["is_active"],
                "is_unmapped": False,
                "values": {},
                "notes": {},
            },
        )
        did = str(r["district_id"])
        course["values"][did] = float(r["z_score"]) if r["z_score"] is not None else None
        if r["notes"]:
            course["notes"][did] = r["notes"]

    # Codeless cutoffs (real z-scores, no Uni-Code) — appended so the admin can
    # SEE the preserved data. Keyed by raw_label since there is no course_code.
    uparams: dict = {"y": year}
    uwhere = "year = :y"
    if q and q.strip():
        uwhere += " AND (raw_label ILIKE :q OR course_name ILIKE :q OR university ILIKE :q)"
        uparams["q"] = f"%{q.strip()}%"
    urows = (
        await db.execute(
            text(
                "SELECT raw_label, course_name, university, district_id, z_score, notes "
                f"FROM unmapped_cutoffs WHERE {uwhere} ORDER BY raw_label"
            ),
            uparams,
        )
    ).mappings().all()
    by_unmapped: dict[str, dict] = {}
    for r in urows:
        row = by_unmapped.setdefault(
            r["raw_label"],
            {
                "course_code": "—",
                "course_number": None,
                "name_en": r["course_name"] or r["raw_label"],
                "university_code": r["university"],
                "is_active": False,
                "is_unmapped": True,
                "values": {},
                "notes": {},
            },
        )
        did = str(r["district_id"])
        row["values"][did] = float(r["z_score"]) if r["z_score"] is not None else None
        if r["notes"]:
            row["notes"][did] = r["notes"]

    all_rows = list(by_course.values()) + list(by_unmapped.values())
    return {
        "year": year,
        "districts": districts,
        "rows": all_rows,
        "total_courses": len(by_course),
        "total_unmapped": len(by_unmapped),
    }


@router.get("/matrix")
async def matrix(
    year: int = Query(...),
    q: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _matrix(db, year, q)


@router.get("/export")
async def export_csv(year: int = Query(...), db: AsyncSession = Depends(get_db)):
    m = await _matrix(db, year, None)
    districts = m["districts"]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["course_code", "course_name", "university"] + [d["name_en"] for d in districts])
    for row in sorted(m["rows"], key=lambda r: r["course_code"]):
        line = [row["course_code"], row["name_en"], row["university_code"] or ""]
        for d in districts:
            v = row["values"].get(str(d["district_id"]))
            line.append("" if v is None else v)
        w.writerow(line)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"content-disposition": f'attachment; filename="cutoffs_{year}.csv"'},
    )
