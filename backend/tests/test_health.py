from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from kritzellm import __version__
from kritzellm.api.routes import health


def test_reports_version_and_models(make_client: Callable[..., TestClient]) -> None:
    client = make_client(transcribe_model="gpt-6-sol", chat_model="gpt-6-luna")
    body = client.get("/health").json()
    assert body["version"] == __version__
    assert body["models"] == {
        "transcribe": "gpt-6-sol",
        "chat": "gpt-6-luna",
        "embed": "text-embedding-3-small",
    }


def test_degraded_when_the_database_is_down(make_client: Callable[..., TestClient]) -> None:
    response = make_client().get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["database"] == "unavailable"


def test_ok_when_the_database_answers(
    make_client: Callable[..., TestClient], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def database_is_up(engine: AsyncEngine) -> bool:
        return True

    monkeypatch.setattr(health, "database_is_up", database_is_up)
    body = make_client().get("/health").json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_engine_is_disposed_on_shutdown(
    make_client: Callable[..., TestClient], monkeypatch: pytest.MonkeyPatch
) -> None:
    disposed: list[AsyncEngine] = []

    async def dispose(self: AsyncEngine, close: bool = True) -> None:
        disposed.append(self)

    monkeypatch.setattr(AsyncEngine, "dispose", dispose)
    with make_client():
        assert disposed == []
    assert len(disposed) == 1
