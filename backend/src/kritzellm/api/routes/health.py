from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncEngine

from kritzellm import __version__
from kritzellm.config import Settings
from kritzellm.db import database_is_up

from ..deps import get_db_engine, get_settings
from ..schemas.health import ConfiguredModels, DependencyStatus, Health, HealthStatus

router = APIRouter(tags=["health"])


@router.get("/health", summary="Check service health", openapi_extra={"security": []})
async def get_health(
    settings: Annotated[Settings, Depends(get_settings)],
    engine: Annotated[AsyncEngine, Depends(get_db_engine)],
) -> Health:
    """Reports whether the service and its database are up, plus the version and configured models.

    Never requires auth. `status` is `degraded` when a dependency is unhealthy.
    """
    database_up = await database_is_up(engine)
    return Health(
        status=HealthStatus.OK if database_up else HealthStatus.DEGRADED,
        version=__version__,
        database=DependencyStatus.OK if database_up else DependencyStatus.UNAVAILABLE,
        models=ConfiguredModels(
            transcribe=settings.transcribe_model,
            chat=settings.chat_model,
            embed=settings.embed_model,
        ),
    )
