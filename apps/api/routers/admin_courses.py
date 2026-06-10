"""Admin course endpoints (Admin Slice 1, Part B2 — masterplan §14.3, §14.1).

GET /api/admin/courses           -- list/filter/paginate (joined with university)
PATCH /api/admin/courses/{code}  -- edit the §14.1 allowlist; bumps updated_at
POST /api/admin/courses          -- add a course (validates university/faculty FKs)

Gated by require_admin; every mutation writes an admin_actions row. Raw SQL
(text()) over the verified courses columns — same approach as B1.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import json_safe_row, log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from core.models.auth import User
from core.schemas.admin_course import (
    CourseCreate,
    CourseListResponse,
    CourseOut,
    CourseUpdate,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:courses"],
    dependencies=[Depends(get_current_admin)],
)

# courses table columns used for RETURNING + audit snapshots (metadata omitted:
# it isn't editable through these endpoints)
_COURSE_COLS = (
    "course_code, course_number, university_id, faculty_id, name_en, name_si, name_ta, "
    "degree_type, duration_years, selection_basis, requires_aptitude_test, description, "
    "career_outlook, is_active, first_intake_year, created_at, updated_at"
)
_UPDATABLE = {
    "name_en", "name_si", "name_ta", "degree_type", "duration_years", "selection_basis",
    "requires_aptitude_test", "description", "career_outlook", "is_active", "first_intake_year",
}
_JOINED_SELECT = (
    f"SELECT {', '.join('c.' + col for col in _COURSE_COLS.split(', '))}, "
    "u.code AS university_code, u.name_en AS university_name_en "
    "FROM courses c LEFT JOIN universities u ON u.university_id = c.university_id"
)


async def _fetch_joined(db: AsyncSession, course_code: str) -> dict | None:
    row = (
        await db.execute(text(f"{_JOINED_SELECT} WHERE c.course_code = :cc"), {"cc": course_code})
    ).mappings().first()
    return json_safe_row(row) if row else None


def _audit_snapshot(joined: dict) -> dict:
    """Course-only columns for the audit log (drop the joined university fields)."""
    return {k: v for k, v in joined.items() if k not in ("university_code", "university_name_en")}


@router.get("/courses", response_model=CourseListResponse)
async def list_courses(
    university_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    selection_basis: str | None = Query(None),
    q: str | None = Query(None, description="substring of course_code or name_en"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> CourseListResponse:
    where, params = [], {}
    if university_id is not None:
        where.append("c.university_id = :uid")
        params["uid"] = university_id
    if is_active is not None:
        where.append("c.is_active = :act")
        params["act"] = is_active
    if selection_basis:
        where.append("c.selection_basis = :sb")
        params["sb"] = selection_basis
    if q:
        where.append("(c.course_code ILIKE :q OR c.name_en ILIKE :q)")
        params["q"] = f"%{q.strip()}%"
    clause = (" WHERE " + " AND ".join(where)) if where else ""

    total = (
        await db.execute(text(f"SELECT count(*) FROM courses c{clause}"), params)
    ).scalar_one()
    rows = (
        await db.execute(
            text(f"{_JOINED_SELECT}{clause} ORDER BY c.course_code LIMIT :limit OFFSET :offset"),
            {**params, "limit": limit, "offset": offset},
        )
    ).mappings().all()
    return CourseListResponse(total=total, items=[CourseOut(**json_safe_row(r)) for r in rows])


@router.post("/courses", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> CourseOut:
    # explicit, friendly validation BEFORE hitting raw FK/PK errors
    if (await db.execute(text("SELECT 1 FROM courses WHERE course_code = :cc"), {"cc": payload.course_code})).first():
        raise HTTPException(status.HTTP_409_CONFLICT, detail=f"Course {payload.course_code} already exists")
    if not (await db.execute(text("SELECT 1 FROM universities WHERE university_id = :id"), {"id": payload.university_id})).first():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Unknown university_id {payload.university_id}")
    if payload.faculty_id is not None and not (
        await db.execute(text("SELECT 1 FROM faculties WHERE faculty_id = :id"), {"id": payload.faculty_id})
    ).first():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Unknown faculty_id {payload.faculty_id}")

    row = (
        await db.execute(
            text(
                f"INSERT INTO courses (course_code, course_number, university_id, faculty_id, "
                f"name_en, name_si, name_ta, degree_type, duration_years, selection_basis, "
                f"requires_aptitude_test, description, career_outlook, is_active, first_intake_year) "
                f"VALUES (:course_code, :course_number, :university_id, :faculty_id, :name_en, "
                f":name_si, :name_ta, :degree_type, :duration_years, :selection_basis, "
                f":requires_aptitude_test, :description, :career_outlook, :is_active, :first_intake_year) "
                f"RETURNING {_COURSE_COLS}"
            ),
            payload.model_dump(),
        )
    ).mappings().one()

    after = json_safe_row(row)
    await log_admin_action(
        db, admin=admin, action_type="course.create", target_table="courses",
        target_id=after["course_code"], before=None, after=after, request=request,
    )
    await db.commit()
    return CourseOut(**(await _fetch_joined(db, payload.course_code)))


@router.patch("/courses/{course_code}", response_model=CourseOut)
async def update_course(
    course_code: str,
    payload: CourseUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> CourseOut:
    code = course_code.strip().upper()
    before_joined = await _fetch_joined(db, code)
    if before_joined is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Course not found")

    fields = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if k in _UPDATABLE}
    if not fields:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail="No updatable fields supplied")

    set_clause = ", ".join(f"{k} = :{k}" for k in fields)  # keys from _UPDATABLE only
    row = (
        await db.execute(
            text(
                f"UPDATE courses SET {set_clause}, updated_at = now() "
                f"WHERE course_code = :course_code RETURNING {_COURSE_COLS}"
            ),
            {**fields, "course_code": code},
        )
    ).mappings().one()

    after = json_safe_row(row)
    await log_admin_action(
        db, admin=admin, action_type="course.update", target_table="courses",
        target_id=code, before=_audit_snapshot(before_joined), after=after, request=request,
    )
    await db.commit()
    return CourseOut(**(await _fetch_joined(db, code)))
