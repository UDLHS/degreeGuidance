"""FastAPI dependencies.

get_db yields an async SQLAlchemy session from the app's AsyncSessionLocal
factory and guarantees it is closed when the request finishes.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from core.db import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
