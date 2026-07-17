"""Admin endpoint for reviewing curated course_requirements rules.

GET /api/admin/requirements       -- read-only list of all baseline subject
                                     rules joined with course names and
                                     eligible stream codes.
GET /api/admin/requirements/gaps  -- Phase 9.5: active course numbers with NO
                                     baseline rule, each carrying what the
                                     book says (verbatim prose + page) so the
                                     note is actionable, not just a red dot.

Listing is read-only: legacy rules come from
data/seeds/course_requirements_data.py (migrated via alembic), and new
courses get their rule at the ingestion gate (Phase 9 D6) — there is still
deliberately no free-form rule editor here.

Gated by require_admin.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_current_admin, get_db
from core.ingestion.artifact_store import load_artifact
from core.ingestion.course_details import details_from_artifact

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


class RequirementGapItem(BaseModel):
    course_number: str
    course_name: str | None
    course_count: int
    #: what the handbook itself says, verbatim — so the admin writes the rule
    #: from the book's words, never from memory
    book_requirements_text: str | None = None
    book_page: int | None = None


class RequirementGapsResponse(BaseModel):
    total: int
    #: the exam year of the book the prose was read from (None = no ingested
    #: book has a course-details artifact yet)
    book_year: int | None
    items: list[RequirementGapItem]


#: Arts (019) is deliberately NOT in course_requirements — its 4-basket
#: selection system has its own dedicated checker (core/eligibility/
#: arts_basket.py), so listing it as a "gap" would be a permanent false flag.
_GAPS_QUERY = text(
    """
    SELECT c.course_number,
           MIN(c.name_en) AS course_name,
           COUNT(*)       AS course_count
    FROM courses c
    WHERE c.is_active
      AND c.course_number IS NOT NULL
      AND c.course_number <> '019'
      AND NOT EXISTS (
          SELECT 1 FROM course_requirements r
          WHERE r.course_number = c.course_number AND r.exam_year IS NULL
      )
    GROUP BY c.course_number
    ORDER BY c.course_number
    """
)


@router.get("/requirements/gaps", response_model=RequirementGapsResponse)
async def requirement_gaps(db: AsyncSession = Depends(get_db)) -> RequirementGapsResponse:
    """Active course numbers the engine serves UNGATED (stream check only).

    Legacy-by-design (migration 24's incremental curation), not an error —
    but each one is exactly the state that let 131's restriction rot in a
    notes field. The book's own wording rides along so closing a gap is one
    read of the prose, not an archaeology dig. Computed live, year-agnostic.
    """
    rows = (await db.execute(_GAPS_QUERY)).all()

    # the newest ingested book that has a course-details artifact
    details = {}
    book_year: int | None = None
    run = (
        await db.execute(
            text(
                "SELECT ir.run_id, ir.year FROM ingestion_runs ir "
                "JOIN ingestion_artifacts ia ON ia.run_id = ir.run_id "
                "WHERE ia.kind = 'course_details.json' "
                "ORDER BY ir.started_at DESC LIMIT 1"
            )
        )
    ).first()
    if run is not None:
        raw = await load_artifact(db, str(run.run_id), "course_details.json")
        if raw is not None:
            details = details_from_artifact(json.loads(raw))
            book_year = run.year

    items = []
    for r in rows:
        d = details.get(r.course_number)
        items.append(
            RequirementGapItem(
                course_number=r.course_number,
                course_name=r.course_name,
                course_count=int(r.course_count),
                book_requirements_text=(d.requirements_text or None) if d else None,
                book_page=d.page_number if d else None,
            )
        )
    return RequirementGapsResponse(total=len(items), book_year=book_year, items=items)


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
