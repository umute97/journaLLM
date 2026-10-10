import asyncio

import pytest
from alembic import command
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from kritzellm.db.migrate import alembic_config

pytestmark = pytest.mark.db

TABLES = {"journals", "pages", "blocks", "chunks", "conversations", "messages"}


async def _query(url: str, sql: str) -> set[str]:
    engine = create_async_engine(url)
    try:
        async with engine.connect() as connection:
            return set((await connection.execute(text(sql))).scalars())
    finally:
        await engine.dispose()


def _tables(url: str) -> set[str]:
    return asyncio.run(_query(url, "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))


def test_fresh_database_reaches_head(database_url: str) -> None:
    assert _tables(database_url) == TABLES | {"alembic_version"}
    extensions = asyncio.run(_query(database_url, "SELECT extname FROM pg_extension"))
    assert {"vector", "pg_trgm"} <= extensions


def test_search_indexes_exist(database_url: str) -> None:
    indexes = asyncio.run(
        _query(database_url, "SELECT indexdef FROM pg_indexes WHERE schemaname = 'public'")
    )
    assert any("USING hnsw (embedding vector_cosine_ops)" in index for index in indexes)
    assert any("USING gin (tsv)" in index for index in indexes)
    assert any("USING gin (text gin_trgm_ops)" in index for index in indexes)


def test_models_match_the_migrations(database_url: str) -> None:
    """Fails when a model changed without a migration (`just db-revision "…"`)."""
    command.check(alembic_config(database_url))


def test_downgrade_and_upgrade_again(database_url: str) -> None:
    config = alembic_config(database_url)
    command.downgrade(config, "base")
    assert _tables(database_url) == {"alembic_version"}
    command.upgrade(config, "head")
    assert _tables(database_url) == TABLES | {"alembic_version"}
