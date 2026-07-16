"""Arq worker settings (Part C2).

Run the background worker with:

    arq apps.worker.settings.WorkerSettings

It connects to the same Redis as the API (settings.redis_url) and registers the
PDF-extraction job. Postgres access inside jobs goes through core.db's
AsyncSessionLocal, exactly like the API.
"""

from __future__ import annotations

from arq.connections import RedisSettings

from apps.worker.jobs.extract_pdf import extract_pdf_job
from apps.worker.jobs.generate_factsheet import generate_factsheet_draft_job
from apps.worker.jobs.index_articles import index_article_job
from apps.worker.jobs.index_factsheets import index_factsheet_job
from core.config import settings


class WorkerSettings:
    functions = [
        extract_pdf_job,
        index_factsheet_job,
        index_article_job,
        generate_factsheet_draft_job,
    ]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    # Arq defaults to 300 s, which killed big-book extractions mid-run (the
    # 15 MB 2025 handbook needs ~8-10 min on a free-tier CPU). See
    # worker_job_timeout_seconds in core/config.py.
    job_timeout = settings.worker_job_timeout_seconds
