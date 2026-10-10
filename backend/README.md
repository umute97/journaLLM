# backend

The Python (FastAPI) service: uploads, transcription, search and the chat agent ✨

It also *defines* the API: [`api/openapi.json`](../api/openapi.json) is generated from the
models and routes in [`src/kritzellm/api`](src/kritzellm/api).

```sh
uv sync                  # install (Python 3.14)
just backend-test        # tests, incl. "is api/openapi.json up to date?" and the DB tests
uv run pyright           # typecheck
just api-export          # regenerate api/openapi.json after changing the API
just backend-dev         # run it with auto-reload on http://localhost:8000 (needs `just up db`)
```

Once it's running, the interactive docs are at <http://localhost:8000/api/v1/docs> 🌸

## Configuration

Everything comes from environment variables (see [`.env.example`](../.env.example)):

| Variable | Default | What it does |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://kritzellm:kritzellm@localhost:5432/kritzellm` | Postgres to use |
| `API_TOKEN` | *(unset)* | When set, every request except `GET /health` needs `Authorization: Bearer <token>` |
| `DATA_DIR` | `data` | Where page images and exports are stored |
| `TRANSCRIBE_MODEL` | `gpt-6-luna` | OpenAI model that reads the pages |
| `CHAT_MODEL` | `gpt-6-luna` | OpenAI model behind the chat agent |
| `EMBED_MODEL` | `text-embedding-3-small` | OpenAI embedding model for search |

Empty values count as unset.

## Database

Postgres with [pgvector](https://github.com/pgvector/pgvector). The tables are SQLAlchemy models in
[`src/kritzellm/db/models.py`](src/kritzellm/db/models.py), and the schema is managed with Alembic.
Migrations live in [`src/kritzellm/db/migrations`](src/kritzellm/db/migrations), so they ship with the image.

```sh
just db-migrate                   # apply migrations to the DATABASE_URL database
just db-revision "add page notes" # generate a migration after changing a model (then read it!)
```

In docker compose, a one-shot `migrate` service applies migrations before `api` starts.

IDs are UUIDv7 `uuid` columns. The models read and write them as the API's TypeIDs (`pg_01k…`),
see [`src/kritzellm/ids.py`](src/kritzellm/ids.py).

**Tests** that need Postgres use `TEST_DATABASE_URL`. Its database is dropped and recreated on every run,
so never point it at real data. `just backend-test` uses `kritzellm_test` in the compose Postgres
(`just up db`). Without a reachable database those tests are skipped; CI sets `KRITZELLM_REQUIRE_DB=1`,
which makes them fail instead. One of them fails when a model changed without a migration.

## Docker

`just up` builds the image from the [`Dockerfile`](Dockerfile) and starts it next to Postgres.
Released images are published as `ghcr.io/umute97/kritzellm-api`; run them with
[`docker-compose.prod.yml`](../docker-compose.prod.yml), which insists on a `POSTGRES_PASSWORD` and an `API_TOKEN`.
