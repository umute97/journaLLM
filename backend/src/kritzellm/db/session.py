"""The async SQLAlchemy engine."""

import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from kritzellm.config import Settings

logger = logging.getLogger(__name__)


def create_engine(settings: Settings) -> AsyncEngine:
    """The engine for the configured database. It connects lazily, on first use."""
    return create_async_engine(str(settings.database_url), pool_pre_ping=True)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


CHECK_TIMEOUT_SECONDS = 2.0


async def database_is_up(engine: AsyncEngine) -> bool:
    """Whether the database answers a trivial query within a couple of seconds."""
    try:
        async with asyncio.timeout(CHECK_TIMEOUT_SECONDS), engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("Database check failed: %r", exc)
        return False
    return True
