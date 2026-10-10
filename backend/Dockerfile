# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.12.22 AS uv

# --- Build: install the app and its dependencies into /app/.venv -----------------------
FROM python:3.14.8-slim-trixie AS build

COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_NO_DEV=1

WORKDIR /app

# Dependencies first, so code changes don't reinstall them.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# --- Runtime: just the virtualenv ---------------------------------------------------------
FROM python:3.14.8-slim-trixie

ARG APP_VERSION=dev
LABEL org.opencontainers.image.title="kritzellm-api" \
      org.opencontainers.image.version="${APP_VERSION}"

RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --no-create-home app \
    && mkdir /data \
    && chown app:app /data

COPY --from=build /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

USER app
WORKDIR /app
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=4)"]

CMD ["uvicorn", "kritzellm.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
