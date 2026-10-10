"""Bring the database schema up to date: `python -m kritzellm.db.migrate`."""

import logging

from alembic import command
from alembic.config import Config


def alembic_config(database_url: str | None = None) -> Config:
    """Alembic's config without an `alembic.ini`, so it works from an installed package too."""
    config = Config()
    config.set_main_option("script_location", "kritzellm.db:migrations")
    if database_url:
        config.attributes["database_url"] = database_url
    return config


def upgrade(database_url: str | None = None) -> None:
    command.upgrade(alembic_config(database_url), "head")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    upgrade()
