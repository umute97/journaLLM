import asyncio
import os
from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from kritzellm.config import Settings
from kritzellm.db.migrate import upgrade
from kritzellm.main import create_app

# Nothing listens on port 1, so connecting fails right away.
UNREACHABLE_DATABASE_URL = "postgresql+asyncpg://kritzellm:kritzellm@127.0.0.1:1/kritzellm"


@pytest.fixture
def make_client() -> Callable[..., TestClient]:
    """Builds an API client whose settings don't depend on the environment (or a local `.env`)."""

    def make(**settings: Any) -> TestClient:
        settings = {"api_token": None, "database_url": UNREACHABLE_DATABASE_URL, **settings}
        return TestClient(create_app(Settings(**settings)), base_url="http://test/api/v1")

    return make


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def _recreate_database(url: str, *, create: bool = True) -> None:
    target = make_url(url)
    admin = create_async_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        async with admin.connect() as connection:
            await connection.execute(
                text(f'DROP DATABASE IF EXISTS "{target.database}" WITH (FORCE)')
            )
            if create:
                await connection.execute(text(f'CREATE DATABASE "{target.database}"'))
    finally:
        await admin.dispose()


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    """A fresh, migrated database from `TEST_DATABASE_URL` (it's dropped and recreated).

    Without one the DB tests are skipped, unless `KRITZELLM_REQUIRE_DB=1` (as in CI).
    """
    url = os.environ.get("TEST_DATABASE_URL")
    required = os.environ.get("KRITZELLM_REQUIRE_DB") == "1"
    try:
        if not url:
            raise LookupError("TEST_DATABASE_URL isn't set")
        asyncio.run(_recreate_database(url))
    except Exception as exc:
        if required:
            raise
        pytest.skip(f"No test database: {exc}")
    upgrade(url)
    yield url
    asyncio.run(_recreate_database(url, create=False))


@pytest.fixture
async def session(database_url: str) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(database_url)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
    await engine.dispose()
