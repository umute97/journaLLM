# backend

The Python (FastAPI) service: uploads, transcription, search and the chat agent ✨

It also *defines* the API: [`api/openapi.json`](../api/openapi.json) is generated from the
models and routes in [`src/kritzellm/api`](src/kritzellm/api).

```sh
uv sync                  # install (Python 3.14)
uv run pytest            # tests, incl. the "is api/openapi.json up to date?" check
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

## Docker

`just up` builds the image from the [`Dockerfile`](Dockerfile) and starts it next to Postgres.
Released images are published as `ghcr.io/umute97/kritzellm-api`; run them with
[`docker-compose.prod.yml`](../docker-compose.prod.yml), which insists on a `POSTGRES_PASSWORD` and an `API_TOKEN`.
