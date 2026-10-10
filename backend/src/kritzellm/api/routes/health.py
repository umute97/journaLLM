from fastapi import APIRouter

from ..errors import not_implemented
from ..schemas.health import Health

router = APIRouter(tags=["health"])


@router.get("/health", summary="Check service health", openapi_extra={"security": []})
async def get_health() -> Health:
    """Reports whether the service and its database are up, plus the version and configured models.

    Never requires auth. `status` is `degraded` when a dependency is unhealthy.
    """
    not_implemented()
