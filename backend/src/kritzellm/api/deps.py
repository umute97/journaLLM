"""Dependencies shared by the routes."""

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine

from kritzellm.config import Settings


def get_settings(request: Request) -> Settings:
    """The settings the running API was created with."""
    return request.app.state.settings


def get_db_engine(request: Request) -> AsyncEngine:
    return request.app.state.db_engine
