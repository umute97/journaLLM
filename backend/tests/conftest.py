from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient

from kritzellm.config import Settings
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
