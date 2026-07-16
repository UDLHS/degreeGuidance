"""Admin factsheet manager (Phase 5 of docs/PHASE2_STUDENT_ADMIN_PLAN.md).

GET  /api/admin/factsheets                    — coverage list: every ACTIVE
       course number (from the live catalog, so future handbook years appear
       automatically) with factsheet + index status:
       missing | not_indexed | stale | indexed
GET  /api/admin/factsheets/{course_number}    — full markdown + index state
PUT  /api/admin/factsheets/{course_number}    — create/update content:
       version bump, hash, audit, auto-enqueue a single-course reindex
POST /api/admin/factsheets/{course_number}/reindex — enqueue reindex only

Drafts (Phase 9.4 — machine-written, human-gated; decisions D3/D4):
POST /api/admin/factsheets/{course_number}/generate-draft — enqueue the worker
       job that writes a draft from book facts + catalog + web enrichment
GET  /api/admin/factsheets/{course_number}/draft           — current draft row
POST /api/admin/factsheets/{course_number}/draft/approve   — copy the (possibly
       admin-edited) draft text into factsheets through the SAME versioned/
       audited/reindexed path as a hand edit, then delete the draft
POST /api/admin/factsheets/{course_number}/draft/reject    — keep the row,
       marked rejected, so the page says what happened

A draft can NEVER reach the index while it is a draft: the index job reads the
factsheets table only, and approve is the single door between the two tables.

The factsheets table is the source of truth (migration 41); the reindex job
re-embeds into document_sources/chunks, which the chat agent's
search_knowledge/lookup_course and the recommender's interest-matching read.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from apps.api.queue import enqueue_generate_factsheet_draft, enqueue_index_factsheet
from core.ingestion.unicode_section import split_label
from core.models.auth import User
from core.models.rag import Factsheet, FactsheetDraft

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:factsheets"],
    dependencies=[Depends(get_current_admin)],
)


class FactsheetListItem(BaseModel):
    course_number: str
    course_name: str          # representative name from the catalog
    course_count: int         # how many Uni-Codes share this course number
    has_factsheet: bool
    version: int | None
    updated_at: datetime | None
    index_status: str         # missing | not_indexed | stale | indexed
    chunk_count: int
    #: queued | ready | failed | rejected | None — a machine draft's state (9.4)
    draft_status: str | None = None


class FactsheetListResponse(BaseModel):
    total: int
    counts: dict[str, int]    # by index_status
    items: list[FactsheetListItem]


class FactsheetDetail(BaseModel):
    course_number: str
    content: str
    version: int
    content_hash: str
    updated_at: datetime
    index_status: str
    chunk_count: int


class FactsheetUpdate(BaseModel):
    content: str = Field(..., min_length=50, max_length=100_000)


class FactsheetDraftOut(BaseModel):
    course_number: str
    status: str               # queued | ready | failed | rejected
    content: str | None
    error: str | None
    provenance: dict | None
    updated_at: datetime


class GenerateDraftRequest(BaseModel):
    #: pins which ingestion run's course_details grounds the draft; None = newest
    run_id: str | None = None


class DraftApproveRequest(BaseModel):
    #: the admin's edited text; None approves the draft exactly as generated
    content: str | None = Field(default=None, min_length=50, max_length=100_000)


class DraftRejectRequest(BaseModel):
    notes: str | None = None


_STATUS_SQL = """
    WITH active_numbers AS (
        SELECT course_number,
               min(name_en) AS course_name,
               count(*)     AS course_count
        FROM courses
        WHERE is_active AND course_number IS NOT NULL
        GROUP BY course_number
    ),
    indexed AS (
        SELECT ds.course_number, ds.content_hash,
               (SELECT count(*) FROM chunks c WHERE c.source_id = ds.source_id) AS chunk_count
        FROM document_sources ds
        WHERE ds.source_type = 'factsheet'
    )
    SELECT an.course_number, an.course_name, an.course_count,
           f.version, f.updated_at, f.content_hash AS fs_hash,
           i.content_hash AS idx_hash, COALESCE(i.chunk_count, 0) AS chunk_count,
           d.status AS draft_status
    FROM active_numbers an
    LEFT JOIN factsheets f ON f.course_number = an.course_number
    LEFT JOIN indexed   i ON i.course_number = an.course_number
    LEFT JOIN factsheet_drafts d ON d.course_number = an.course_number
    ORDER BY an.course_number
"""


def _index_status(fs_hash: str | None, idx_hash: str | None) -> str:
    if fs_hash is None:
        return "missing"
    if idx_hash is None:
        return "not_indexed"
    return "indexed" if fs_hash == idx_hash else "stale"


@router.get("/factsheets", response_model=FactsheetListResponse)
async def list_factsheets(db: AsyncSession = Depends(get_db)) -> FactsheetListResponse:
    rows = (await db.execute(text(_STATUS_SQL))).mappings().all()
    items = []
    counts: dict[str, int] = {}
    for r in rows:
        status_ = _index_status(r["fs_hash"], r["idx_hash"])
        counts[status_] = counts.get(status_, 0) + 1
        # A factsheet covers the whole course of study, not one campus — strip
        # the representative catalog name's trailing "(University …)" so
        # "Medicine (Eastern University, Sri Lanka)" lists as just "Medicine".
        # split_label removes only the LAST parenthetical, so names like
        # "Applied Sciences (Biological Sc.) (Rajarata …)" keep their real
        # qualifier: "Applied Sciences (Biological Sc.)".
        clean_name = split_label(r["course_name"])[0] or r["course_name"]
        items.append(
            FactsheetListItem(
                course_number=r["course_number"],
                course_name=clean_name,
                course_count=r["course_count"],
                has_factsheet=r["fs_hash"] is not None,
                version=r["version"],
                updated_at=r["updated_at"],
                index_status=status_,
                chunk_count=r["chunk_count"],
                draft_status=r["draft_status"],
            )
        )
    return FactsheetListResponse(total=len(items), counts=counts, items=items)


async def _detail(db: AsyncSession, course_number: str) -> FactsheetDetail:
    row = await db.get(Factsheet, course_number)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No factsheet for this course number")
    idx = (
        await db.execute(
            text(
                "SELECT ds.content_hash, "
                "(SELECT count(*) FROM chunks c WHERE c.source_id = ds.source_id) AS n "
                "FROM document_sources ds "
                "WHERE ds.source_type = 'factsheet' AND ds.course_number = :cn"
            ),
            {"cn": course_number},
        )
    ).first()
    return FactsheetDetail(
        course_number=row.course_number,
        content=row.content,
        version=row.version,
        content_hash=row.content_hash,
        updated_at=row.updated_at,
        index_status=_index_status(row.content_hash, idx[0] if idx else None),
        chunk_count=idx[1] if idx else 0,
    )


@router.get("/factsheets/{course_number}", response_model=FactsheetDetail)
async def get_factsheet(
    course_number: str, db: AsyncSession = Depends(get_db)
) -> FactsheetDetail:
    return await _detail(db, course_number)


async def _require_known_course(db: AsyncSession, course_number: str) -> None:
    known = (
        await db.execute(
            text("SELECT 1 FROM courses WHERE course_number = :cn LIMIT 1"),
            {"cn": course_number},
        )
    ).first()
    if not known:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Unknown course number {course_number!r} — not in the catalog.",
        )


async def _save_content(
    db: AsyncSession,
    admin: User,
    course_number: str,
    content: str,
    request: Request,
    *,
    notes: str | None = None,
) -> bool:
    """Create/update the factsheets row + audit — the ONE write path shared by
    a hand edit and a draft approval, so both get versioning, hashing and the
    audit trail identically. Does NOT commit. Returns False for a no-op save
    (same hash: no version bump, no reindex needed)."""
    new_hash = hashlib.sha256(content.encode()).hexdigest()
    row = await db.get(Factsheet, course_number)
    if row is None:
        row = Factsheet(
            course_number=course_number,
            content=content,
            content_hash=new_hash,
            version=1,
            updated_by=admin.user_id,
        )
        db.add(row)
        action, before = "factsheet.create", None
    else:
        if row.content_hash == new_hash:
            return False
        before = {"version": row.version, "content_hash": row.content_hash}
        row.content = content
        row.content_hash = new_hash
        row.version = row.version + 1
        row.updated_by = admin.user_id
        row.updated_at = datetime.now(timezone.utc)
        action = "factsheet.update"

    await log_admin_action(
        db, admin=admin, action_type=action,
        target_table="factsheets", target_id=course_number,
        before=before,
        after={"version": row.version, "content_hash": new_hash, "chars": len(content)},
        request=request, notes=notes,
    )
    return True


@router.put("/factsheets/{course_number}", response_model=FactsheetDetail)
async def upsert_factsheet(
    course_number: str,
    payload: FactsheetUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> FactsheetDetail:
    course_number = course_number.strip()
    await _require_known_course(db, course_number)

    changed = await _save_content(db, admin, course_number, payload.content, request)
    if not changed:
        # No-op save: nothing changes, no version bump, no reindex.
        return await _detail(db, course_number)
    await db.commit()
    # Auto-reindex so the agent/recommender see the edit (worker does the embeds)
    await enqueue_index_factsheet(course_number=course_number)
    return await _detail(db, course_number)


@router.post("/factsheets/{course_number}/reindex")
async def reindex_factsheet(
    course_number: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> dict:
    row = await db.get(Factsheet, course_number)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No factsheet for this course number")
    await log_admin_action(
        db, admin=admin, action_type="factsheet.reindex",
        target_table="factsheets", target_id=course_number,
        before=None, after={"content_hash": row.content_hash}, request=request,
    )
    await db.commit()
    await enqueue_index_factsheet(course_number=course_number)
    return {"enqueued": True, "course_number": course_number}


# ── Drafts (Phase 9.4) — machine-written, human-gated ────────────────────────

def _draft_out(row: FactsheetDraft) -> FactsheetDraftOut:
    return FactsheetDraftOut(
        course_number=row.course_number,
        status=row.status,
        content=row.content,
        error=row.error,
        provenance=row.provenance,
        updated_at=row.updated_at,
    )


@router.post("/factsheets/{course_number}/generate-draft", response_model=FactsheetDraftOut)
async def generate_draft(
    course_number: str,
    payload: GenerateDraftRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> FactsheetDraftOut:
    """Enqueue the worker job that writes a draft for this course of study.
    Replaces any previous draft (ready/failed/rejected); refuses while one is
    already being generated."""
    course_number = course_number.strip()
    await _require_known_course(db, course_number)

    row = await db.get(FactsheetDraft, course_number)
    if row is not None and row.status == "queued":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="A draft is already being generated for this course.",
        )
    if row is None:
        row = FactsheetDraft(course_number=course_number)
        db.add(row)
    row.status = "queued"
    row.content = None
    row.error = None
    row.provenance = {"run_id": payload.run_id} if payload.run_id else None
    row.requested_by = admin.user_id
    row.updated_at = datetime.now(timezone.utc)

    await log_admin_action(
        db, admin=admin, action_type="factsheet.draft_generate",
        target_table="factsheet_drafts", target_id=course_number,
        before=None, after={"run_id": payload.run_id}, request=request,
    )
    await db.commit()
    await enqueue_generate_factsheet_draft(
        course_number=course_number, run_id=payload.run_id
    )
    await db.refresh(row)
    return _draft_out(row)


@router.get("/factsheets/{course_number}/draft", response_model=FactsheetDraftOut)
async def get_draft(
    course_number: str, db: AsyncSession = Depends(get_db)
) -> FactsheetDraftOut:
    row = await db.get(FactsheetDraft, course_number.strip())
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No draft for this course number")
    return _draft_out(row)


@router.post("/factsheets/{course_number}/draft/approve", response_model=FactsheetDetail)
async def approve_draft(
    course_number: str,
    payload: DraftApproveRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> FactsheetDetail:
    """The one door between drafts and the live factsheet (D4): copies the
    (possibly admin-edited) text into factsheets via the same versioned/audited
    write path as a hand edit, deletes the draft in the same transaction, and
    only then does the reindex land it in the advisor's knowledge base."""
    course_number = course_number.strip()
    row = await db.get(FactsheetDraft, course_number)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No draft for this course number")
    if row.status != "ready":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"Draft is not ready for review (status={row.status}).",
        )
    content = payload.content if payload.content is not None else row.content
    if not content or len(content.strip()) < 50:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Draft content is empty."
        )

    changed = await _save_content(
        db, admin, course_number, content, request,
        notes="approved machine draft (Phase 9.4)",
    )
    edited = payload.content is not None and payload.content != row.content
    await log_admin_action(
        db, admin=admin, action_type="factsheet.draft_approve",
        target_table="factsheet_drafts", target_id=course_number,
        before={"status": row.status, "provenance": row.provenance},
        after={"edited_before_approve": edited, "chars": len(content)},
        request=request,
    )
    await db.delete(row)
    await db.commit()
    if changed:
        await enqueue_index_factsheet(course_number=course_number)
    return await _detail(db, course_number)


@router.post("/factsheets/{course_number}/draft/reject", response_model=FactsheetDraftOut)
async def reject_draft(
    course_number: str,
    payload: DraftRejectRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> FactsheetDraftOut:
    """Keep the row, marked rejected, so the page says what happened (and the
    next generate replaces it)."""
    course_number = course_number.strip()
    row = await db.get(FactsheetDraft, course_number)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No draft for this course number")
    if row.status not in ("ready", "failed"):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"Only a ready or failed draft can be rejected (status={row.status}).",
        )
    before = row.status
    row.status = "rejected"
    row.updated_at = datetime.now(timezone.utc)
    await log_admin_action(
        db, admin=admin, action_type="factsheet.draft_reject",
        target_table="factsheet_drafts", target_id=course_number,
        before={"status": before}, after={"status": "rejected"},
        request=request, notes=payload.notes,
    )
    await db.commit()
    await db.refresh(row)
    return _draft_out(row)
