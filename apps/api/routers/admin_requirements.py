"""Admin endpoint for reviewing curated course_requirements rules.

GET /api/admin/requirements  -- read-only list of all baseline subject rules
                               joined with course names and eligible stream codes.
                               Used by the admin requirements review page.

This endpoint is intentionally read-only: the source of truth is
data/seeds/course_requirements_data.py (migrated via alembic). Edits go
through that file + a new migration, not through an API.

Gated by require_admin.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_current_admin, get_db

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:requirements"],
    dependencies=[Depends(get_current_admin)],
)


class RequirementOut(BaseModel):
    course_number: str
    course_name: str | None
    source_section: str | None
    notes: str | None
    ol_requirements: str | None
    subject_rule: dict
    eligible_stream_codes: list[str]


_QUERY = text(
    """
    SELECT
        cr.course_number,
        MIN(c.name_en)                                          AS course_name,
        cr.source_section,
        cr.notes,
        cr.ol_requirements,
        cr.subject_rule,
        ARRAY_REMOVE(ARRAY_AGG(DISTINCT s.code ORDER BY s.code), NULL)
                                                                AS eligible_stream_codes
    FROM course_requirements cr
    LEFT JOIN courses c
           ON c.course_number = cr.course_number AND c.is_active = TRUE
    LEFT JOIN course_stream_eligibility cse ON cse.course_code = c.course_code
    LEFT JOIN streams s ON s.stream_id = cse.stream_id
    WHERE cr.exam_year IS NULL
    GROUP BY cr.course_number, cr.source_section, cr.notes,
             cr.ol_requirements, cr.subject_rule
    ORDER BY cr.course_number
    """
)

_QUERY_FILTERED = text(
    """
    SELECT
        cr.course_number,
        MIN(c.name_en)                                          AS course_name,
        cr.source_section,
        cr.notes,
        cr.ol_requirements,
        cr.subject_rule,
        ARRAY_REMOVE(ARRAY_AGG(DISTINCT s.code ORDER BY s.code), NULL)
                                                                AS eligible_stream_codes
    FROM course_requirements cr
    LEFT JOIN courses c
           ON c.course_number = cr.course_number AND c.is_active = TRUE
    LEFT JOIN course_stream_eligibility cse ON cse.course_code = c.course_code
    LEFT JOIN streams s ON s.stream_id = cse.stream_id
    WHERE cr.exam_year IS NULL
      AND (
          cr.course_number ILIKE :q
          OR c.name_en ILIKE :q
          OR cr.source_section ILIKE :q
      )
    GROUP BY cr.course_number, cr.source_section, cr.notes,
             cr.ol_requirements, cr.subject_rule
    ORDER BY cr.course_number
    """
)


@router.get("/requirements", response_model=list[RequirementOut])
async def list_requirements(
    q: str | None = Query(None, description="Filter by course number, name, or source section"),
    db: AsyncSession = Depends(get_db),
) -> list[RequirementOut]:
    if q and q.strip():
        rows = (
            await db.execute(_QUERY_FILTERED, {"q": f"%{q.strip()}%"})
        ).mappings().all()
    else:
        rows = (await db.execute(_QUERY)).mappings().all()

    return [
        RequirementOut(
            course_number=r["course_number"],
            course_name=r["course_name"],
            source_section=r["source_section"],
            notes=r["notes"],
            ol_requirements=r["ol_requirements"],
            subject_rule=r["subject_rule"],
            eligible_stream_codes=list(r["eligible_stream_codes"] or []),
        )
        for r in rows
    ]
