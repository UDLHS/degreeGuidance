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
from apps.worker.jobs.index_factsheets import index_factsheet_job
from core.config import settings


class WorkerSettings:
    functions = [extract_pdf_job, index_factsheet_job]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
