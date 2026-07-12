"""Article indexing job (Phase 8.6).

Admin-authored knowledge beyond courses (aptitude-test guides, UGC
procedures, scholarship rules) — read from the ARTICLES table and indexed
into the chat agent's knowledge base through the exact machinery factsheets
use: H2-section chunking, gemini-embedding-001, document_sources + chunks.
Identity: (source_type='article', file_path='db:articles/<id>').

Idempotent like the factsheet job: unchanged content (same SHA-256) is
skipped; changed articles have their chunks replaced. The admin Articles
editor enqueues 'index_article_job' on every save; deletion is handled
synchronously in the router (DB-only, no embedding needed).
"""

from __future__ import annotations

import time

from dotenv import load_dotenv

load_dotenv()

from google import genai  # noqa: E402
from sqlalchemy import delete, select  # noqa: E402

from apps.worker.jobs.index_factsheets import (  # noqa: E402
    RATE_LIMIT_DELAY,
    _chunk_factsheet,
    _embed_one,
    _sha256,
)
from core.config import settings  # noqa: E402
from core.db import AsyncSessionLocal  # noqa: E402
from core.models.rag import Article, Chunk, DocumentSource  # noqa: E402


def _article_path(article_id: int) -> str:
    return f"db:articles/{article_id}"


async def index_article(
    session, client: genai.Client, article_id: int, force: bool = False
) -> tuple[int, bool]:
    """Index one article. Returns (chunks_written, was_skipped)."""
    row = await session.get(Article, article_id)
    if row is None:
        raise ValueError(f"No article row for id {article_id!r}")

    content_hash = row.content_hash or _sha256(row.content)

    existing = await session.scalar(
        select(DocumentSource).where(
            DocumentSource.source_type == "article",
            DocumentSource.file_path == _article_path(article_id),
            DocumentSource.content_hash == content_hash,
        )
    )
    if existing and not force:
        return 0, True  # unchanged — skip

    stale_rows = (
        await session.scalars(
            select(DocumentSource).where(
                DocumentSource.source_type == "article",
                DocumentSource.file_path == _article_path(article_id),
            )
        )
    ).all()
    for stale in stale_rows:
        await session.execute(delete(Chunk).where(Chunk.source_id == stale.source_id))
        await session.delete(stale)
    if stale_rows:
        await session.flush()

    source = DocumentSource(
        source_type="article",
        course_number=None,
        title=row.title,
        file_path=_article_path(article_id),
        content_hash=content_hash,
    )
    session.add(source)
    await session.flush()

    # Prepend the title so the first chunk carries it (mirrors factsheets,
    # where chunk 0 is the H1 title block — retrieval quality depends on it).
    chunks = _chunk_factsheet(f"# {row.title}\n\n{row.content}")
    if not chunks:
        return 0, False

    for i, chunk_data in enumerate(chunks):
        embedding = _embed_one(client, chunk_data.content)
        session.add(Chunk(
            source_id=source.source_id,
            chunk_index=chunk_data.index,
            heading=chunk_data.heading,
            content=chunk_data.content,
            token_count=len(chunk_data.content.split()),
            embedding=embedding,
        ))
        if i < len(chunks) - 1:
            time.sleep(RATE_LIMIT_DELAY)

    return len(chunks), False


async def remove_article_index(session, article_id: int) -> int:
    """Drop an article's document_source + chunks (delete path — DB-only,
    callable from the router synchronously). Returns sources removed."""
    stale_rows = (
        await session.scalars(
            select(DocumentSource).where(
                DocumentSource.source_type == "article",
                DocumentSource.file_path == _article_path(article_id),
            )
        )
    ).all()
    for stale in stale_rows:
        await session.execute(delete(Chunk).where(Chunk.source_id == stale.source_id))
        await session.delete(stale)
    return len(stale_rows)


# ── Arq job: (re)index one article after an admin save ──────────────────────

async def index_article_job(ctx, article_id: int) -> dict:
    client = genai.Client(api_key=settings.gemini_api_key)
    async with AsyncSessionLocal() as session:
        chunks, skipped = await index_article(session, client, article_id)
        await session.commit()
    return {"article_id": article_id, "chunks": chunks, "skipped": skipped}
