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


async def enqueue_extract_pdf(*, run_id: str, pdf_path: str, exam_year: int) -> None:
    """Enqueue the PDF-extraction job for the worker to pick up."""
    pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await pool.enqueue_job(
            "extract_pdf_job", run_id=run_id, pdf_path=pdf_path, exam_year=exam_year
        )
    finally:
        await pool.aclose()
