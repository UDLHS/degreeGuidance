"""Public reference-data endpoint (Week 3, Part 1 UI).

GET /api/v1/reference — districts, streams, universities, straight from the DB.
No auth (same public tier as eligibility/recommendations). Lets the frontend
populate its pickers from the real catalog instead of hardcoding values that
could drift from the schema (e.g. the actual 6 A/L streams + the ICT
navigation category — masterplan §3).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_db
from core.models.reference import District, Stream, University
from core.schemas.reference import (
    DistrictOut,
    ReferenceResponse,
    StreamOut,
    UniversityOut,
)

router = APIRouter(prefix="/api/v1", tags=["reference"])


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
