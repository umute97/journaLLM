from pathlib import Path

import pytest

from kritzellm.config import Settings

VARS = ("DATABASE_URL", "API_TOKEN", "DATA_DIR", "TRANSCRIBE_MODEL", "CHAT_MODEL", "EMBED_MODEL")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in VARS:
        monkeypatch.delenv(var, raising=False)


def test_defaults() -> None:
    settings = Settings()
    assert str(settings.database_url).startswith("postgresql+asyncpg://")
    assert settings.api_token is None
    assert settings.data_dir == Path("data")
    assert settings.transcribe_model == "gpt-6-luna"
    assert settings.chat_model == "gpt-6-luna"
    assert settings.embed_model == "text-embedding-3-small"


def test_reads_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_TOKEN", "s3cret")
    monkeypatch.setenv("DATA_DIR", "/data")
    monkeypatch.setenv("CHAT_MODEL", "gpt-6-sol")
    settings = Settings()
    assert settings.api_token is not None
    assert settings.api_token.get_secret_value() == "s3cret"
    assert settings.data_dir == Path("/data")
    assert settings.chat_model == "gpt-6-sol"


def test_empty_values_fall_back_to_the_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """`.env.example` ships `API_TOKEN=` and friends; empty means "not set"."""
    defaults = Settings()
    for var in VARS:
        monkeypatch.setenv(var, "")
    assert Settings() == defaults


def test_rejects_a_non_postgres_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "mysql://nope@localhost/nope")
    with pytest.raises(ValueError, match="database_url"):
        Settings()


def test_token_is_hidden_in_reprs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_TOKEN", "s3cret")
    assert "s3cret" not in repr(Settings())
