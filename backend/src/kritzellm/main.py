"""The ASGI app: the API lives under `/api/v1` (the web app will be served next to it)."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.app import API_PREFIX, create_api
from .config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    api = create_api(settings or get_settings())

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        yield
        await api.state.db_engine.dispose()

    app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None, lifespan=lifespan)
    app.mount(API_PREFIX, api)
    return app


app = create_app()
