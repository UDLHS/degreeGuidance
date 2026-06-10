"""Admin alias endpoints (Admin Slice 1, Part B1 — masterplan §14.3).

GET/POST/PATCH/DELETE /api/admin/aliases — manage course_aliases: list/filter,
add, correct, verify, delete. Every route is gated by require_admin; every
mutation appends an admin_actions row (before/after JSONB).

Uses raw SQL (text()) against the verified course_aliases columns, consistent
with the Phase 6 eligibility engine — no dependency on ORM models for that table.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import json_safe_row, log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from core.models.auth import User
from core.schemas.admin import AliasCreate, AliasListResponse, AliasOut, AliasUpdate

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:aliases"],
    dependencies=[Depends(get_current_admin)],  # gate every route in this router
)

_COLS = "alias_id, course_code, alias_text, source, confidence, is_verified, created_at"
_UPDATABLE = {"alias_text", "source", "confidence", "is_verified"}


async def _fetch_alias(db: AsyncSession, alias_id: int) -> dict | None:
    row = (
        await db.execute(
            text(f"SELECT {_COLS} FROM course_aliases WHERE alias_id = :id"), {"id": alias_id}
        )
    ).mappings().first()
    return json_safe_row(row) if row else None


@router.get("/aliases", response_model=AliasListResponse)
async def list_aliases(
    course_code: str | None = Query(None),
    is_verified: bool | None = Query(None),
    q: str | None = Query(None, description="case-insensitive substring of alias_text"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> AliasListResponse:
    where, params = [], {}
    if course_code:
        where.append("course_code = :cc")
        params["cc"] = course_code.strip().upper()
    if is_verified is not None:
        where.append("is_verified = :v")
        params["v"] = is_verified
    if q:
        where.append("alias_text ILIKE :q")
        params["q"] = f"%{q.strip()}%"
    clause = (" WHERE " + " AND ".join(where)) if where else ""

    total = (
        await db.execute(text(f"SELECT count(*) FROM course_aliases{clause}"), params)
    ).scalar_one()
    rows = (
        await db.execute(
            text(
                f"SELECT {_COLS} FROM course_aliases{clause} "
                f"ORDER BY alias_id LIMIT :limit OFFSET :offset"
            ),
            {**params, "limit": limit, "offset": offset},
        )
    ).mappings().all()
    return AliasListResponse(total=total, items=[AliasOut(**json_safe_row(r)) for r in rows])


@router.post("/aliases", response_model=AliasOut, status_code=status.HTTP_201_CREATED)
async def create_alias(
    payload: AliasCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> AliasOut:
    course = (
        await db.execute(
            text("SELECT 1 FROM courses WHERE course_code = :cc"), {"cc": payload.course_code}
        )
    ).first()
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Unknown course_code: {payload.course_code}",
        )
    try:
        row = (
            await db.execute(
                text(
                    f"INSERT INTO course_aliases (course_code, alias_text, source, confidence, is_verified) "
                    f"VALUES (:cc, :at, :src, :conf, :ver) RETURNING {_COLS}"
                ),
                {
                    "cc": payload.course_code,
                    "at": payload.alias_text,
                    "src": payload.source,
                    "conf": payload.confidence,
                    "ver": payload.is_verified,
                },
            )
        ).mappings().one()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alias already exists for {payload.course_code}",
        )

    after = json_safe_row(row)
    await log_admin_action(
        db, admin=admin, action_type="alias.create", target_table="course_aliases",
        target_id=after["alias_id"], before=None, after=after, request=request,
    )
    await db.commit()
    return AliasOut(**after)


@router.patch("/aliases/{alias_id}", response_model=AliasOut)
async def update_alias(
    alias_id: int,
    payload: AliasUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> AliasOut:
    before = await _fetch_alias(db, alias_id)
    if before is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alias not found")

    fields = payload.model_dump(exclude_unset=True)
    fields = {k: v for k, v in fields.items() if k in _UPDATABLE}
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="No updatable fields supplied"
        )

    set_clause = ", ".join(f"{k} = :{k}" for k in fields)  # keys are from _UPDATABLE only
    try:
        row = (
            await db.execute(
                text(f"UPDATE course_aliases SET {set_clause} WHERE alias_id = :id RETURNING {_COLS}"),
                {**fields, "id": alias_id},
            )
        ).mappings().one()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Alias text collides with an existing alias"
        )

    after = json_safe_row(row)
    await log_admin_action(
        db, admin=admin, action_type="alias.update", target_table="course_aliases",
        target_id=alias_id, before=before, after=after, request=request,
    )
    await db.commit()
    return AliasOut(**after)


@router.delete("/aliases/{alias_id}")
async def delete_alias(
    alias_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> dict:
    before = await _fetch_alias(db, alias_id)
    if before is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alias not found")

    await db.execute(text("DELETE FROM course_aliases WHERE alias_id = :id"), {"id": alias_id})
    await log_admin_action(
        db, admin=admin, action_type="alias.delete", target_table="course_aliases",
        target_id=alias_id, before=before, after=None, request=request,
    )
    await db.commit()
    return {"deleted": alias_id}
