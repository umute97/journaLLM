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
check:
    pre-commit run --all-files

# --- API contract (coming soon) --------------------------------------------------

# Lint the OpenAPI spec
api-lint:
    @echo "Not yet: arrives with the OpenAPI contract."

# Serve a mock API from the spec
api-mock:
    @echo "Not yet: arrives with the OpenAPI contract."

# Preview the API docs
api-docs:
    @echo "Not yet: arrives with the OpenAPI contract."
