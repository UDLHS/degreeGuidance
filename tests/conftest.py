"""Pytest fixtures for the eligibility test suite (masterplan v4 §16.1).

Design choices that matter:
- A FRESH async engine is created per test (NullPool) and disposed after. This
  binds each connection pool to that test's own event loop, sidestepping the
  classic "Future attached to a different loop" problem you hit when a single
  module-level engine is reused across pytest-asyncio's per-test loops. Slightly
  slower, but bulletproof across pytest-asyncio versions.
- Tests run against the DEV database (same DATABASE_URL) because that is where
  the real 6,525 cutoff rows live. The cases are read-only on the core tables.
- The engine writes one eligibility_audit row per call. The autouse
  `_isolate_audit` fixture records MAX(audit_id) before each test and deletes
  only rows created during it, so your real audit history is preserved and the
  engine itself is never modified.
"""

from __future__ import annotations

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from core.config import settings


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(settings.database_url, poolclass=NullPool)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def _isolate_audit(engine):
    """Delete only eligibility_audit rows created during this test."""
    async with AsyncSession(engine, expire_on_commit=False) as s:
        before = (
            await s.execute(text("SELECT COALESCE(MAX(audit_id), 0) FROM eligibility_audit"))
        ).scalar_one()
    yield
    async with AsyncSession(engine, expire_on_commit=False) as s:
        await s.execute(
            text("DELETE FROM eligibility_audit WHERE audit_id > :before"),
            {"before": before},
        )
        await s.commit()


@pytest_asyncio.fixture
async def client(engine):
    """httpx client wired to the FastAPI app, with get_db overridden onto the
    test engine so API tests share the per-test loop."""
    from httpx import ASGITransport, AsyncClient

    from apps.api.dependencies import get_db
    from apps.api.main import app

    async def _override_get_db():
        async with AsyncSession(engine, expire_on_commit=False) as s:
            yield s

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
