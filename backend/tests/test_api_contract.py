import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from kritzellm.api.app import render_openapi
from kritzellm.main import create_app

SPEC_PATH = Path(__file__).resolve().parents[2] / "api" / "openapi.json"

JOURNAL_ID = "jrn_01k7c8x2v4f6g8h9j0k1m2n3p4"
PAGE_ID = "pg_01k7c9a3b5d7e9f1g3h5j7k9m1"
BLOCK_ID = "blk_01k7c9b4c6e8f0g2h4j6k8m0n2"
CONVERSATION_ID = "cnv_01k7cbc5d7f9g1h3j5k7m9n1p3"
JOB_ID = "job_01k7c9a4c6e8g0h2j4k6m8n0p2"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app(), base_url="http://test/api/v1")


def _without_version(spec: str) -> dict:
    data = json.loads(spec)
    data["info"].pop("version", None)
    return data


def test_committed_spec_matches_the_code() -> None:
    """api/openapi.json must be regenerated (`just api-export`) whenever the API changes."""
    assert SPEC_PATH.exists(), "api/openapi.json is missing. Run `just api-export`."
    # The version is stamped by release-please, so it may run ahead of the installed package.
    assert _without_version(SPEC_PATH.read_text()) == _without_version(render_openapi()), (
        "api/openapi.json is out of date. Run `just api-export`."
    )


def test_spec_writes_whole_numbers_like_javascript() -> None:
    """release-please rewrites the spec with JSON.stringify, which writes `1.0` as `1`."""
    assert not re.search(r":\s-?\d+\.0\b", render_openapi())


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("GET", "/health", None),
        ("GET", "/journals", None),
        ("POST", "/journals", {"name": "Summer 2026"}),
        ("GET", f"/journals/{JOURNAL_ID}", None),
        ("PATCH", f"/journals/{JOURNAL_ID}", {"name": "Summer 2026 🌻"}),
        ("DELETE", f"/journals/{JOURNAL_ID}", None),
        ("POST", f"/journals/{JOURNAL_ID}/exports", {"format": "markdown"}),
        ("GET", "/pages", None),
        ("GET", f"/pages/{PAGE_ID}", None),
        ("PATCH", f"/pages/{PAGE_ID}", {"entryDates": ["2026-07-14"]}),
        ("DELETE", f"/pages/{PAGE_ID}", None),
        ("GET", f"/pages/{PAGE_ID}/image", None),
        ("PUT", f"/pages/{PAGE_ID}/blocks", {"blocks": []}),
        ("POST", f"/pages/{PAGE_ID}/transcribe", None),
        ("GET", f"/blocks/{BLOCK_ID}", None),
        ("PATCH", f"/blocks/{BLOCK_ID}", {"text": "fixed"}),
        ("GET", f"/blocks/{BLOCK_ID}/image", None),
        ("GET", "/search?q=lisbon", None),
        ("GET", "/conversations", None),
        ("POST", "/conversations", None),
        ("GET", f"/conversations/{CONVERSATION_ID}", None),
        ("PATCH", f"/conversations/{CONVERSATION_ID}", {"title": "Lisbon"}),
        ("DELETE", f"/conversations/{CONVERSATION_ID}", None),
        ("POST", f"/conversations/{CONVERSATION_ID}/messages", {"content": "hi"}),
        ("GET", "/jobs", None),
        ("GET", f"/jobs/{JOB_ID}", None),
        ("GET", f"/jobs/{JOB_ID}/result", None),
        ("POST", "/admin/reindex", None),
    ],
)
def test_stubs_answer_501_problem(
    client: TestClient, method: str, path: str, body: dict | None
) -> None:
    response = client.request(method, path, json=body)
    assert response.status_code == 501
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["title"] == "Not Implemented"


def test_every_operation_has_a_stub_test() -> None:
    spec = json.loads(render_openapi())
    operations = sum(len(methods) for methods in spec["paths"].values())
    tested = len(test_stubs_answer_501_problem.pytestmark[0].args[1])
    # Uploads (multipart) are covered separately below.
    assert tested == operations - 1


def test_upload_stub_answers_501(client: TestClient) -> None:
    files = [
        ("files", ("p1.jpg", b"fake", "image/jpeg")),
        ("files", ("p2.jpg", b"fake", "image/jpeg")),
    ]
    response = client.post(
        f"/journals/{JOURNAL_ID}/pages", files=files, data={"startPageNumber": "3"}
    )
    assert response.status_code == 501


def test_malformed_ids_are_422_problems(client: TestClient) -> None:
    response = client.get("/pages/not-a-page-id")
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert [error["parameter"] for error in response.json()["errors"]] == ["pageId"]


def test_invalid_query_values_name_the_parameter(client: TestClient) -> None:
    response = client.get("/pages?journalId=nope&limit=0")
    assert response.status_code == 422
    assert {error["parameter"] for error in response.json()["errors"]} == {"journalId", "limit"}


def test_invalid_body_fields_point_at_the_field(client: TestClient) -> None:
    response = client.post("/journals", json={"name": "", "nope": 1})
    assert response.status_code == 422
    pointers = {error["pointer"] for error in response.json()["errors"]}
    assert pointers == {"/name", "/nope"}


def test_malformed_json_is_400(client: TestClient) -> None:
    response = client.post(
        "/journals", content=b"{not json", headers={"content-type": "application/json"}
    )
    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"


def test_unknown_routes_are_404_problems(client: TestClient) -> None:
    response = client.get("/nope")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
