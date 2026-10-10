# Task runner: https://just.systems (`brew install just`). Run `just` to list recipes.

set dotenv-load := true

# List all recipes
default:
    @just --list --unsorted

# --- Local stack ---------------------------------------------------------------

# Start the local stack in the background (rebuilds the api image if needed)
up:
    docker compose up -d --wait --build

# Stop the local stack (data is kept)
down:
    docker compose down

# Follow logs (optionally for one service)
logs service="":
    docker compose logs -f {{ service }}

# Open psql inside the database container
psql:
    docker compose exec db psql -U "${POSTGRES_USER:-kritzellm}" -d "${POSTGRES_DB:-kritzellm}"

# Check the database is up and speaks pgvector
db-check:
    @docker compose exec -T db psql -U "${POSTGRES_USER:-kritzellm}" -d "${POSTGRES_DB:-kritzellm}" -v ON_ERROR_STOP=1 -tA \
        -c "SELECT 'postgres ' || current_setting('server_version') || ', pgvector ' || default_version FROM pg_available_extensions WHERE name = 'vector';"

# Check the running API answers on /health and /docs
api-check:
    @curl -fsS "http://localhost:${API_PORT:-8000}/api/v1/health" && echo
    @curl -fsS -o /dev/null "http://localhost:${API_PORT:-8000}/api/v1/docs" && echo "docs ok"

# Delete the local database and data volumes (asks first)
[confirm("This deletes all local database data and page images. Continue?")]
db-reset:
    docker compose down -v

# --- Quality ---------------------------------------------------------------------

# Run every check (grows as components land)
check: backend-lint backend-typecheck backend-test api-lint
    pre-commit run --all-files

# --- Backend ---------------------------------------------------------------------

# Lint and format-check the backend
backend-lint:
    cd backend && uv run ruff check . && uv run ruff format --check .

# Typecheck the backend
backend-typecheck:
    cd backend && uv run pyright

# Run the backend tests
backend-test:
    cd backend && uv run pytest

# Run the API locally with auto-reload, against the compose database (`just up db`)
backend-dev:
    uv run --project backend uvicorn kritzellm.main:app --reload --reload-dir backend/src --port "${API_PORT:-8000}"

# --- API contract ----------------------------------------------------------------

# Regenerate api/openapi.json from the backend code
api-export:
    cd backend && uv run python scripts/export_openapi.py

# Install the API contract tooling (Redocly, Prism, Scalar)
api-install:
    npm --prefix api ci

# Lint the OpenAPI spec
api-lint:
    npm --prefix api run lint

# Serve a mock API (random but valid data) on http://localhost:4010
api-mock:
    npm --prefix api run mock

# Preview the API docs on http://localhost:4011
api-docs:
    npm --prefix api run docs
