"""Arq enqueue helpers for the API process (Part C2).

Kept behind a thin function so the upload route doesn't construct Arq pools
inline — and so tests can monkeypatch enqueue without a live Redis. The worker
process holds the long-lived pool; the API opens a short-lived one per enqueue
(admin uploads are rare, so this is simpler than managing an app-lifecycle pool).
"""

from __future__ import annotations

from arq import create_pool
from arq.connections import RedisSettings

from core.config import settings


async def enqueue_extract_pdf(
    *, run_id: str, pdf_path: str, exam_year: int, cutoff_pages: str | None = None
) -> None:
    """Enqueue the PDF-extraction job for the worker to pick up.

    cutoff_pages carries the admin-supplied page ranges on manual re-extraction
    (e.g. '150-156,179-188'); None lets the extractor auto-detect.
    """
    pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await pool.enqueue_job(
            "extract_pdf_job",
            run_id=run_id,
            pdf_path=pdf_path,
            exam_year=exam_year,
            cutoff_pages=cutoff_pages,
        )
    finally:
        await pool.aclose()


async def enqueue_index_factsheet(*, course_number: str) -> None:
    """Enqueue a single-course factsheet reindex (admin Factsheets save path)."""
    pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await pool.enqueue_job("index_factsheet_job", course_number=course_number)
    finally:
        await pool.aclose()


async def enqueue_generate_factsheet_draft(
    *, course_number: str, run_id: str | None = None
) -> None:
    """Enqueue factsheet-draft generation (Phase 9.4). run_id pins which book's
    course_details the draft is grounded in; None uses the newest ingested."""
    pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await pool.enqueue_job(
            "generate_factsheet_draft_job", course_number=course_number, run_id=run_id
        )
    finally:
        await pool.aclose()


async def enqueue_index_article(*, article_id: int) -> None:
    """Enqueue a single-article reindex (admin Articles save path — Phase 8.6)."""
    pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await pool.enqueue_job("index_article_job", article_id=article_id)
    finally:
        await pool.aclose()
