"""Dependencies shared by the routes."""

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from kritzellm.config import Settings


def get_settings(request: Request) -> Settings:
    """The settings the running API was created with."""
    return request.app.state.settings


def get_db_engine(request: Request) -> AsyncEngine:
    return request.app.state.db_engine


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """A database session for one request. Routes commit their own changes."""
    async with request.app.state.sessionmaker() as session:
        yield session
