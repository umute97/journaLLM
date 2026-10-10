"""The ASGI app: the API lives under `/api/v1` (the web app will be served next to it)."""

from fastapi import FastAPI

from .api.app import API_PREFIX, create_api


def create_app() -> FastAPI:
    app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
    app.mount(API_PREFIX, create_api())
    return app


app = create_app()
