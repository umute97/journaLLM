"""Server settings, read from environment variables (see `.env.example`)."""

from functools import lru_cache
from pathlib import Path

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_ignore_empty=True, extra="ignore")

    database_url: PostgresDsn = PostgresDsn(
        "postgresql+asyncpg://kritzellm:kritzellm@localhost:5432/kritzellm"
    )
    """SQLAlchemy URL of the Postgres database."""
    api_token: SecretStr | None = None
    """When set, every API request (except `/health`) needs `Authorization: Bearer <token>`."""
    data_dir: Path = Path("data")
    """Where page images and exports are stored."""

    transcribe_model: str = "gpt-6-luna"
    """OpenAI model that reads page images."""
    chat_model: str = "gpt-6-luna"
    """OpenAI model behind the chat agent."""
    embed_model: str = "text-embedding-3-small"
    """OpenAI embedding model used for search."""


@lru_cache
def get_settings() -> Settings:
    return Settings()
