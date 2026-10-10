"""Alembic environment: runs migrations against `DATABASE_URL` (or the URL `migrate.py` passes in)."""

import asyncio
from typing import Any, Literal

from alembic import context
from alembic.autogenerate.api import AutogenContext
from pgvector.sqlalchemy import Vector
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from kritzellm.config import Settings
from kritzellm.db.models import Base
from kritzellm.db.types import TypeId

config = context.config


def render_item(type_: str, obj: Any, autogen_context: AutogenContext) -> str | Literal[False]:
    """Write our column types as plain Postgres types, so migrations don't import app code."""
    if type_ == "type" and isinstance(obj, TypeId):
        autogen_context.imports.add("from sqlalchemy.dialects import postgresql")
        return "postgresql.UUID(as_uuid=True)"
    if type_ == "type" and isinstance(obj, Vector):
        autogen_context.imports.add("import pgvector.sqlalchemy")
        return f"pgvector.sqlalchemy.Vector({obj.dim})"
    return False


def configure(**kwargs: Any) -> None:
    context.configure(target_metadata=Base.metadata, render_item=render_item, **kwargs)


def run(connection: Connection) -> None:
    configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()


async def run_online(url: str) -> None:
    engine = create_async_engine(url)
    async with engine.connect() as connection:
        await connection.run_sync(run)
    await engine.dispose()


url = config.attributes.get("database_url") or str(Settings().database_url)
if context.is_offline_mode():
    configure(url=url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_online(url))
