"""Public reference-data endpoint (Week 3, Part 1 UI).

GET /api/v1/reference — districts, streams, universities, straight from the DB.
No auth (same public tier as eligibility/recommendations). Lets the frontend
populate its pickers from the real catalog instead of hardcoding values that
could drift from the schema (e.g. the actual 6 A/L streams + the ICT
navigation category — masterplan §3).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_db
from core.models.reference import District, Stream, University
from core.schemas.reference import (
    CutoffHistoryResponse,
    DistrictOut,
    ExamYearOut,
    ReferenceResponse,
    StreamOut,
    UniversityOut,
    YearsResponse,
)

router = APIRouter(prefix="/api/v1", tags=["reference"])


@router.get("/years", response_model=YearsResponse)
async def get_years(db: AsyncSession = Depends(get_db)) -> YearsResponse:
    """Exam years that have promoted cutoff data, newest first.

    Sourced from z_score_cutoffs (the promoted store) — a year exists here
    exactly when the admin promoted that year's handbook, so this list always
    matches what the eligibility engine can actually serve. The latest year is
    the engine's default when a request carries no exam_year.
    """
    rows = (
        await db.execute(
            text("SELECT DISTINCT year FROM z_score_cutoffs ORDER BY year DESC")
        )
    ).scalars().all()
    return YearsResponse(
        years=[ExamYearOut(year=y, is_latest=(i == 0)) for i, y in enumerate(rows)]
    )


@router.get("/cutoff-history", response_model=CutoffHistoryResponse)
async def get_cutoff_history(
    district_code: str,
    stream_code: str,
    db: AsyncSession = Depends(get_db),
) -> CutoffHistoryResponse:
    """Every course's effective cutoff per promoted year for one district +
    stream, in a single call (a per-course endpoint would mean 100+ requests
    from the results page). Stream overrides are COALESCEd exactly like the
    eligibility engine, so the trend a student sees matches the cutoff they
    were actually judged against. NQC/absent years are simply missing keys.
    """
    district_code = district_code.strip().upper()
    stream_code = stream_code.strip().upper()
    did = (
        await db.execute(
            text("SELECT district_id FROM districts WHERE code = :c"), {"c": district_code}
        )
    ).scalar()
    sid = (
        await db.execute(
            text("SELECT stream_id FROM streams WHERE code = :c"), {"c": stream_code}
        )
    ).scalar()
    if did is None or sid is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Unknown {'district' if did is None else 'stream'} code",
        )

    rows = (
        await db.execute(
            text(
                """
                SELECT zc.course_code, zc.year,
                       COALESCE(so.z_score, zc.z_score) AS z_score
                FROM z_score_cutoffs zc
                LEFT JOIN course_stream_cutoff_overrides so
                       ON so.course_code = zc.course_code
                      AND so.district_id = zc.district_id
                      AND so.year        = zc.year
                      AND so.stream_id   = :s
                WHERE zc.district_id = :d
                  AND COALESCE(so.z_score, zc.z_score) IS NOT NULL
                """
            ),
            {"d": did, "s": sid},
        )
    ).all()

    years: set[int] = set()
    courses: dict[str, dict[str, float]] = {}
    for code, year, z in rows:
        years.add(year)
        courses.setdefault(code, {})[str(year)] = float(z)

    return CutoffHistoryResponse(
        district_code=district_code,
        stream_code=stream_code,
        years=sorted(years, reverse=True),
        courses=courses,
    )


@router.get("/reference", response_model=ReferenceResponse)
async def get_reference(db: AsyncSession = Depends(get_db)) -> ReferenceResponse:
    districts = (
        await db.scalars(select(District).order_by(District.name_en))
    ).all()
    streams = (await db.scalars(select(Stream).order_by(Stream.stream_id))).all()
    universities = (
        await db.scalars(select(University).order_by(University.code))
    ).all()

    subject_rows = (
        await db.execute(
            text(
                "SELECT s.code AS stream_code, sub.name_en AS subject_name "
                "FROM stream_subjects ss "
                "JOIN streams s ON s.stream_id = ss.stream_id "
                "JOIN subjects sub ON sub.subject_id = ss.subject_id "
                "ORDER BY s.code, sub.name_en"
            )
        )
    ).mappings().all()
    subjects_by_stream: dict[str, list[str]] = {}
    for row in subject_rows:
        subjects_by_stream.setdefault(row["stream_code"], []).append(row["subject_name"])

    return ReferenceResponse(
        districts=[
            DistrictOut(code=d.code, name_en=d.name_en, is_disadvantaged=d.is_disadvantaged)
            for d in districts
        ],
        streams=[
            StreamOut(
                code=s.code,
                name_en=s.name_en,
                description=s.description,
                subjects=subjects_by_stream.get(s.code, []),
            )
            for s in streams
        ],
        universities=[
            UniversityOut(code=u.code, name_en=u.name_en, short_name=u.short_name)
            for u in universities
        ],
    )
