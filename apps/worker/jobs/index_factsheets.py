"""Factsheet indexing job.

Reads all markdown factsheets from content/factsheets/, chunks them by H2
section, embeds each chunk with gemini-embedding-001 (768 dims via Matryoshka),
and upserts into document_sources + chunks tables.

Re-running is idempotent: unchanged files (same SHA-256 hash) are skipped;
changed files have their chunks deleted and re-indexed.

Usage (from project root):
    python -m apps.worker.jobs.index_factsheets
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
from core.models.rag import Chunk, DocumentSource  # noqa: E402

FACTSHEETS_DIR = Path(__file__).parents[3] / "content" / "factsheets"
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


async def index_file(
    session,
    client: genai.Client,
    path: Path,
    force: bool = False,
) -> tuple[int, bool]:
    """Index a single factsheet. Returns (chunks_written, was_skipped)."""
    raw = path.read_text(encoding="utf-8")
    content_hash = _sha256(raw)
    course_number = _extract_course_number(path.name)
    title = _extract_title(raw, path.name)

    # Check if already indexed with same content
    existing = await session.scalar(
        select(DocumentSource).where(DocumentSource.content_hash == content_hash)
    )
    if existing and not force:
        return 0, True  # unchanged — skip

    # Delete stale record if content changed
    stale = await session.scalar(
        select(DocumentSource).where(DocumentSource.file_path == str(path))
    )
    if stale:
        await session.execute(
            delete(Chunk).where(Chunk.source_id == stale.source_id)
        )
        await session.delete(stale)
        await session.flush()

    # Create new document source record
    source = DocumentSource(
        source_type="factsheet",
        course_number=course_number,
        title=title,
        file_path=str(path),
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


async def run(force: bool = False) -> None:
    factsheets = sorted(FACTSHEETS_DIR.glob("*.md"))
    if not factsheets:
        print(f"No factsheets found in {FACTSHEETS_DIR}")
        return

    client = genai.Client(api_key=settings.gemini_api_key)
    print(f"Indexing {len(factsheets)} factsheets into database…")

    total_chunks = 0
    skipped = 0

    async with AsyncSessionLocal() as session:
        for i, path in enumerate(factsheets, 1):
            try:
                n, was_skipped = await index_file(session, client, path, force=force)
                if was_skipped:
                    print(f"  [{i:2}/{len(factsheets)}] SKIP  {path.name} (unchanged)")
                    skipped += 1
                else:
                    print(f"  [{i:2}/{len(factsheets)}] OK    {path.name}  ({n} chunks)")
                    total_chunks += n

                await session.commit()

            except Exception as e:
                await session.rollback()
                print(f"  [{i:2}/{len(factsheets)}] ERROR {path.name}: {e}")

    print(f"\nDone. {total_chunks} chunks written, {skipped} files skipped (unchanged).")


if __name__ == "__main__":
    force = "--force" in sys.argv
    asyncio.run(run(force=force))
