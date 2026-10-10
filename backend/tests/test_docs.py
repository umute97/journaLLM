from collections.abc import Callable

from fastapi.testclient import TestClient

from kritzellm.api.routes.docs import SCALAR_INTEGRITY, SCALAR_URL


def test_docs_page_loads_pinned_scalar(make_client: Callable[..., TestClient]) -> None:
    response = make_client().get("/docs")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert f'src="{SCALAR_URL}" integrity="{SCALAR_INTEGRITY}"' in response.text
    assert 'data-url="openapi.json"' in response.text
    assert "@scalar/api-reference@" in SCALAR_URL


def test_spec_is_served_next_to_the_docs(make_client: Callable[..., TestClient]) -> None:
    response = make_client().get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "kritzeLLM API"


def test_no_swagger_or_redoc(make_client: Callable[..., TestClient]) -> None:
    client = make_client()
    assert "swagger" not in client.get("/docs").text.lower()
    assert client.get("/redoc").status_code == 404
