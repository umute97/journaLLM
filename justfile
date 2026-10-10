# Task runner: https://just.systems (`brew install just`). Run `just` to list recipes.

set dotenv-load := true

# List all recipes
default:
    @just --list --unsorted

# --- Local stack ---------------------------------------------------------------

# Start the local stack in the background
up:
    docker compose up -d --wait

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

# Delete the local database volume (asks first)
[confirm("This deletes all local database data. Continue?")]
db-reset:
    docker compose down -v

# --- Quality ---------------------------------------------------------------------

# Run every check (grows as components land)
check: backend-lint backend-test api-lint
    pre-commit run --all-files

# --- Backend ---------------------------------------------------------------------

# Lint and format-check the backend
backend-lint:
    cd backend && uv run ruff check . && uv run ruff format --check .

# Run the backend tests
backend-test:
    cd backend && uv run pytest

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
