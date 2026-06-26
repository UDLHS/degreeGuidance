"""SQLAlchemy engine and session factory.

`Base` is the declarative base every ORM model inherits from.
`engine` is the async engine used by the app.
`AsyncSessionLocal` is the session factory used in FastAPI endpoints and worker jobs.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class Base(DeclarativeBase):
    """Base class all ORM models inherit from."""


_connect_args = {"ssl": True} if settings.environment == "production" else {}

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args=_connect_args,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
