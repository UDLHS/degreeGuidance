"""Knowledge-base browser (Phase 6 of docs/PHASE2_STUDENT_ADMIN_PLAN.md).

GET  /api/admin/knowledge                     — indexed sources + chunk/embedding
                                                counts + stale-vs-factsheet flags
GET  /api/admin/knowledge/{source_id}/chunks  — read-only chunk inspector
POST /api/admin/knowledge/reindex-stale       — enqueue single-course reindex jobs
                                                for every stale / never-indexed
                                                factsheet (audited)

Read-only except the reindex trigger. Stale = factsheets.content_hash differs
from the indexed document_sources.content_hash — the exact signal the chat
agent's search_knowledge quality depends on.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from apps.api.queue import enqueue_index_factsheet
from core.models.auth import User

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:knowledge"],
    dependencies=[Depends(get_current_admin)],
)


class SourceItem(BaseModel):
    source_id: int
    source_type: str
    course_number: str | None
    title: str
    indexed_at: datetime
    chunk_count: int
    embedded_count: int
    stale: bool               # factsheet content changed since this index
    orphaned: bool            # indexed but no factsheets row anymore


class KnowledgeResponse(BaseModel):
    totals: dict[str, int]    # sources, chunks, embedded_chunks, stale, never_indexed
    items: list[SourceItem]
    never_indexed: list[str]  # factsheet course_numbers with no index at all


class ChunkItem(BaseModel):
    chunk_index: int
    heading: str | None
    token_count: int | None
    has_embedding: bool
    content: str


@router.get("/knowledge", response_model=KnowledgeResponse)
async def list_knowledge(db: AsyncSession = Depends(get_db)) -> KnowledgeResponse:
    rows = (
        await db.execute(
            text(
                """
                SELECT ds.source_id, ds.source_type, ds.course_number, ds.title,
                       ds.indexed_at, ds.content_hash AS idx_hash,
                       f.content_hash AS fs_hash,
                       (SELECT count(*) FROM chunks c WHERE c.source_id = ds.source_id) AS chunk_count,
                       (SELECT count(*) FROM chunks c
                         WHERE c.source_id = ds.source_id AND c.embedding IS NOT NULL) AS embedded_count
                FROM document_sources ds
                LEFT JOIN factsheets f ON f.course_number = ds.course_number
                ORDER BY ds.course_number NULLS LAST, ds.source_id
                """
            )
        )
    ).mappings().all()

    items = []
    stale_n = 0
    for r in rows:
        stale = r["fs_hash"] is not None and r["fs_hash"] != r["idx_hash"]
        if stale:
            stale_n += 1
        items.append(
            SourceItem(
                source_id=r["source_id"],
                source_type=r["source_type"],
                course_number=r["course_number"],
                title=r["title"],
                indexed_at=r["indexed_at"],
                chunk_count=r["chunk_count"],
                embedded_count=r["embedded_count"],
                stale=stale,
                orphaned=r["fs_hash"] is None,
            )
        )

    never = (
        await db.execute(
            text(
                "SELECT f.course_number FROM factsheets f "
                "WHERE NOT EXISTS (SELECT 1 FROM document_sources ds "
                "  WHERE ds.source_type = 'factsheet' AND ds.course_number = f.course_number) "
                "ORDER BY f.course_number"
            )
        )
    ).scalars().all()

    totals = {
        "sources": len(items),
        "chunks": sum(i.chunk_count for i in items),
        "embedded_chunks": sum(i.embedded_count for i in items),
        "stale": stale_n,
        "never_indexed": len(never),
    }
    return KnowledgeResponse(totals=totals, items=items, never_indexed=list(never))


@router.get("/knowledge/{source_id}/chunks", response_model=list[ChunkItem])
async def inspect_chunks(
    source_id: int, db: AsyncSession = Depends(get_db)
) -> list[ChunkItem]:
    exists = (
        await db.execute(
            text("SELECT 1 FROM document_sources WHERE source_id = :s"), {"s": source_id}
        )
    ).first()
    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Source not found")
    rows = (
        await db.execute(
            text(
                "SELECT chunk_index, heading, token_count, "
                "(embedding IS NOT NULL) AS has_embedding, content "
                "FROM chunks WHERE source_id = :s ORDER BY chunk_index"
            ),
            {"s": source_id},
        )
    ).mappings().all()
    return [
        ChunkItem(
            chunk_index=r["chunk_index"],
            heading=r["heading"],
            token_count=r["token_count"],
            has_embedding=r["has_embedding"],
            content=r["content"],
        )
        for r in rows
    ]


@router.post("/knowledge/reindex-stale")
async def reindex_stale(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> dict:
    """Enqueue a single-course reindex for every factsheet that is stale or has
    never been indexed. Unchanged factsheets are untouched (the job itself is
    also hash-idempotent, so double-enqueueing is harmless)."""
    numbers = (
        await db.execute(
            text(
                """
                SELECT f.course_number FROM factsheets f
                LEFT JOIN document_sources ds
                       ON ds.source_type = 'factsheet'
                      AND ds.course_number = f.course_number
                WHERE ds.source_id IS NULL OR ds.content_hash <> f.content_hash
                ORDER BY f.course_number
                """
            )
        )
    ).scalars().all()

    for cn in numbers:
        await enqueue_index_factsheet(course_number=cn)

    await log_admin_action(
        db, admin=admin, action_type="knowledge.reindex_stale",
        target_table="factsheets", target_id="*",
        before=None, after={"enqueued": len(numbers), "course_numbers": list(numbers)[:50]},
        request=request,
    )
    await db.commit()
    return {"enqueued": len(numbers), "course_numbers": list(numbers)}
