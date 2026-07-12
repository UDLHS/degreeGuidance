"""Admin knowledge articles (Phase 8.6 — user request 2026-07-12).

Knowledge beyond courses: aptitude-test guides, UGC procedures, scholarship
rules, deadlines. Stored in the ARTICLES table and indexed into the chat
agent's knowledge base through the same machinery factsheets use.

GET    /api/admin/articles            — list with index-staleness state
GET    /api/admin/articles/{id}       — full content for the editor
POST   /api/admin/articles            — create (audited, auto-enqueues index)
PUT    /api/admin/articles/{id}       — update (version bump, audited, reindex)
DELETE /api/admin/articles/{id}       — delete row + its index (audited)

Save semantics mirror the factsheet editor: no-op saves don't bump versions
or reindex; content_hash vs document_sources.content_hash is the staleness
signal the Knowledge page displays.
"""

from __future__ import annotations

import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from apps.api.queue import enqueue_index_article
from apps.worker.jobs.index_articles import remove_article_index
from core.models.auth import User
from core.models.rag import Article

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:articles"],
    dependencies=[Depends(get_current_admin)],
)


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


class ArticleListItem(BaseModel):
    article_id: int
    title: str
    version: int
    updated_at: datetime
    index_status: str  # 'indexed' | 'stale' | 'never_indexed'


class ArticleListResponse(BaseModel):
    total: int
    items: list[ArticleListItem]


class ArticleDetail(BaseModel):
    article_id: int
    title: str
    content: str
    version: int
    content_hash: str
    updated_at: datetime
    index_status: str


class ArticleWrite(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=200_000)


def _index_status(row_hash: str, idx_hash: str | None) -> str:
    if idx_hash is None:
        return "never_indexed"
    return "indexed" if idx_hash == row_hash else "stale"


async def _idx_hash(db: AsyncSession, article_id: int) -> str | None:
    return (
        await db.execute(
            text(
                "SELECT content_hash FROM document_sources "
                "WHERE source_type = 'article' AND file_path = :p"
            ),
            {"p": f"db:articles/{article_id}"},
        )
    ).scalar()


@router.get("/articles", response_model=ArticleListResponse)
async def list_articles(db: AsyncSession = Depends(get_db)) -> ArticleListResponse:
    rows = (
        await db.execute(
            text(
                """
                SELECT a.article_id, a.title, a.version, a.updated_at,
                       a.content_hash, ds.content_hash AS idx_hash
                FROM articles a
                LEFT JOIN document_sources ds
                  ON ds.source_type = 'article'
                 AND ds.file_path = 'db:articles/' || a.article_id
                ORDER BY a.updated_at DESC
                """
            )
        )
    ).mappings().all()
    items = [
        ArticleListItem(
            article_id=r["article_id"],
            title=r["title"],
            version=r["version"],
            updated_at=r["updated_at"],
            index_status=_index_status(r["content_hash"], r["idx_hash"]),
        )
        for r in rows
    ]
    return ArticleListResponse(total=len(items), items=items)


@router.get("/articles/{article_id}", response_model=ArticleDetail)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)) -> ArticleDetail:
    row = await db.get(Article, article_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Article not found")
    return ArticleDetail(
        article_id=row.article_id,
        title=row.title,
        content=row.content,
        version=row.version,
        content_hash=row.content_hash,
        updated_at=row.updated_at,
        index_status=_index_status(row.content_hash, await _idx_hash(db, article_id)),
    )


@router.post("/articles", response_model=ArticleDetail, status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleWrite,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> ArticleDetail:
    row = Article(
        title=payload.title.strip(),
        content=payload.content,
        content_hash=_sha256(payload.content),
        updated_by=admin.user_id,
    )
    db.add(row)
    await db.flush()
    await log_admin_action(
        db, admin=admin, action_type="article.create", target_table="articles",
        target_id=str(row.article_id), before=None,
        after={"title": row.title, "version": 1, "content_hash": row.content_hash},
        request=request,
    )
    await db.commit()
    await enqueue_index_article(article_id=row.article_id)
    return ArticleDetail(
        article_id=row.article_id, title=row.title, content=row.content,
        version=row.version, content_hash=row.content_hash, updated_at=row.updated_at,
        index_status="never_indexed",
    )


@router.put("/articles/{article_id}", response_model=ArticleDetail)
async def update_article(
    article_id: int,
    payload: ArticleWrite,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> ArticleDetail:
    row = await db.get(Article, article_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Article not found")

    new_hash = _sha256(payload.content)
    changed = row.content_hash != new_hash or row.title != payload.title.strip()
    if changed:
        before = {"title": row.title, "version": row.version, "content_hash": row.content_hash}
        row.title = payload.title.strip()
        row.content = payload.content
        row.content_hash = new_hash
        row.version = row.version + 1
        row.updated_by = admin.user_id
        await db.execute(
            text("UPDATE articles SET updated_at = now() WHERE article_id = :id"),
            {"id": article_id},
        )
        await log_admin_action(
            db, admin=admin, action_type="article.update", target_table="articles",
            target_id=str(article_id), before=before,
            after={"title": row.title, "version": row.version, "content_hash": new_hash},
            request=request,
        )
        await db.commit()
        await enqueue_index_article(article_id=article_id)
    # no-op saves: nothing changes, no version bump, no reindex (factsheet parity)

    return await get_article(article_id, db)


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> None:
    row = await db.get(Article, article_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Article not found")
    removed_sources = await remove_article_index(db, article_id)
    before = {"title": row.title, "version": row.version, "content_hash": row.content_hash}
    await db.delete(row)
    await log_admin_action(
        db, admin=admin, action_type="article.delete", target_table="articles",
        target_id=str(article_id), before=before,
        after={"index_sources_removed": removed_sources}, request=request,
    )
    await db.commit()
