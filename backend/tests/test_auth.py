from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

TOKEN = "s3cret"


@pytest.fixture
def client(make_client: Callable[..., TestClient]) -> TestClient:
    return make_client(api_token=SecretStr(TOKEN))


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer nope"},
        {"Authorization": f"Bearer {TOKEN}x"},
        {"Authorization": f"Basic {TOKEN}"},
    ],
    ids=["missing", "wrong", "longer", "not-bearer"],
)
def test_wrong_or_missing_token_is_401(client: TestClient, headers: dict[str, str]) -> None:
    response = client.get("/journals", headers=headers)
    assert response.status_code == 401
    assert response.headers["content-type"] == "application/problem+json"
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["title"] == "Unauthorized"


def test_right_token_gets_through(client: TestClient) -> None:
    response = client.get("/journals", headers={"Authorization": f"Bearer {TOKEN}"})
    assert response.status_code == 501  # past auth; the route itself isn't built yet


def test_auth_comes_before_validation(client: TestClient) -> None:
    response = client.get("/pages/not-a-page-id")
    assert response.status_code == 401


@pytest.mark.parametrize("path", ["/health", "/docs", "/openapi.json"])
def test_some_paths_never_need_a_token(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 200


def test_everything_is_open_without_a_configured_token(
    make_client: Callable[..., TestClient],
) -> None:
    response = make_client().get("/journals")
    assert response.status_code == 501
