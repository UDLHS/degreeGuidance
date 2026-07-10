"""Factsheet indexing job.

Reads factsheet markdown from the FACTSHEETS TABLE (the source of truth since
migration 41 — decision D3; content/factsheets/*.md is only the git seed),
chunks by H2 section, embeds each chunk with gemini-embedding-001 (768 dims
via Matryoshka), and upserts into document_sources + chunks.

Re-running is idempotent: unchanged rows (same SHA-256 content_hash) are
skipped; changed rows have their chunks deleted and re-indexed. A single
course can be reindexed via index_course() / the 'index_factsheet_job' Arq
job — the admin Factsheets page enqueues it on every save.

Usage (from project root):
    python -m apps.worker.jobs.index_factsheets            # all, skip unchanged
    python -m apps.worker.jobs.index_factsheets --force    # re-embed everything
"""

from __future__ import annotations

import asyncio
import hashlib
import re
import sys
import time
from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv

load_dotenv()

from google import genai  # noqa: E402
from google.genai.types import EmbedContentConfig  # noqa: E402
from sqlalchemy import delete, select, text  # noqa: E402
from sqlalchemy.dialects.postgresql import insert as pg_insert  # noqa: E402

from core.config import settings  # noqa: E402
from core.db import AsyncSessionLocal  # noqa: E402
from core.models.rag import Chunk, DocumentSource, Factsheet  # noqa: E402

FACTSHEETS_DIR = Path(__file__).parents[3] / "content" / "factsheets"  # git seed only
RATE_LIMIT_DELAY = 0.7   # seconds between each individual embed call (85/min, under 100 free-tier limit)
MAX_CHUNK_CHARS = 2000    # ~400-500 tokens per chunk


class ChunkData(NamedTuple):
    index: int
    heading: str | None
    content: str


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _extract_course_number(filename: str) -> str:
    """'001.md' → '001'"""
    return Path(filename).stem


def _extract_title(content: str, filename: str) -> str:
    """Extract H1 title from markdown, fallback to filename."""
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return filename


def _chunk_factsheet(content: str) -> list[ChunkData]:
    """Split markdown into chunks by H2 section.

    Each H2 section becomes one chunk. If a section exceeds MAX_CHUNK_CHARS,
    it's split on double-newline paragraph boundaries.
    """
    sections = re.split(r"\n(?=## )", content)
    chunks: list[ChunkData] = []
    idx = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue

        heading: str | None = None
        body = section
        if section.startswith("## "):
            lines = section.split("\n", 1)
            heading = lines[0][3:].strip()
            body = lines[1].strip() if len(lines) > 1 else ""

        if not body:
            continue

        if len(body) <= MAX_CHUNK_CHARS:
            chunks.append(ChunkData(idx, heading, body))
            idx += 1
        else:
            # Split long sections on paragraphs
            paragraphs = [p.strip() for p in re.split(r"\n\n+", body) if p.strip()]
            current = ""
            for para in paragraphs:
                if current and len(current) + len(para) + 2 > MAX_CHUNK_CHARS:
                    chunks.append(ChunkData(idx, heading, current))
                    idx += 1
                    current = para
                else:
                    current = f"{current}\n\n{para}".strip() if current else para
            if current:
                chunks.append(ChunkData(idx, heading, current))
                idx += 1

    return chunks


def _embed_one(client: genai.Client, text: str) -> list[float]:
    """Embed a single text. Caller is responsible for rate-limiting between calls."""
    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=text,
        config=EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=settings.gemini_embedding_dim,
        ),
    )
    return result.embeddings[0].values


async def index_row(
    session,
    client: genai.Client,
    row: Factsheet,
    force: bool = False,
) -> tuple[int, bool]:
    """Index one factsheets row. Returns (chunks_written, was_skipped)."""
    raw = row.content
    content_hash = row.content_hash or _sha256(raw)
    title = _extract_title(raw, f"{row.course_number}.md")

    # Already indexed with identical content? (idempotency)
    existing = await session.scalar(
        select(DocumentSource).where(
            DocumentSource.source_type == "factsheet",
            DocumentSource.course_number == row.course_number,
            DocumentSource.content_hash == content_hash,
        )
    )
    if existing and not force:
        return 0, True  # unchanged — skip

    # Replace any stale index for this course (matches pre-migration rows that
    # carried a file_path too — course_number is the stable identity).
    stale_rows = (
        await session.scalars(
            select(DocumentSource).where(
                DocumentSource.source_type == "factsheet",
                DocumentSource.course_number == row.course_number,
            )
        )
    ).all()
    for stale in stale_rows:
        await session.execute(delete(Chunk).where(Chunk.source_id == stale.source_id))
        await session.delete(stale)
    if stale_rows:
        await session.flush()

    source = DocumentSource(
        source_type="factsheet",
        course_number=row.course_number,
        title=title,
        file_path=f"db:factsheets/{row.course_number}",
        content_hash=content_hash,
    )
    session.add(source)
    await session.flush()  # get source_id

    chunks = _chunk_factsheet(raw)
    if not chunks:
        return 0, False

    # Embed each chunk individually with rate-limit delay
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


async def index_course(
    session, client: genai.Client, course_number: str, force: bool = False
) -> tuple[int, bool]:
    """Reindex a single course's factsheet from the DB (admin save path)."""
    row = await session.get(Factsheet, course_number)
    if row is None:
        raise ValueError(f"No factsheet row for course number {course_number!r}")
    return await index_row(session, client, row, force=force)


async def run(force: bool = False) -> None:
    client = genai.Client(api_key=settings.gemini_api_key)
    total_chunks = 0
    skipped = 0

    async with AsyncSessionLocal() as session:
        rows = (
            await session.scalars(select(Factsheet).order_by(Factsheet.course_number))
        ).all()
        if not rows:
            print("No factsheets in the DB (run migration 41 / seed first).")
            return
        print(f"Indexing {len(rows)} factsheets from the DB…")
        for i, row in enumerate(rows, 1):
            try:
                n, was_skipped = await index_row(session, client, row, force=force)
                if was_skipped:
                    print(f"  [{i:3}/{len(rows)}] SKIP  {row.course_number} (unchanged)")
                    skipped += 1
                else:
                    print(f"  [{i:3}/{len(rows)}] OK    {row.course_number}  ({n} chunks)")
                    total_chunks += n
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"  [{i:3}/{len(rows)}] ERROR {row.course_number}: {e}")

    print(f"\nDone. {total_chunks} chunks written, {skipped} rows skipped (unchanged).")


# ── Arq job: reindex one course after an admin edit ──────────────────────────

async def index_factsheet_job(ctx, course_number: str) -> dict:
    client = genai.Client(api_key=settings.gemini_api_key)
    async with AsyncSessionLocal() as session:
        chunks, skipped = await index_course(session, client, course_number)
        await session.commit()
    return {"course_number": course_number, "chunks": chunks, "skipped": skipped}


if __name__ == "__main__":
    force = "--force" in sys.argv
    asyncio.run(run(force=force))
