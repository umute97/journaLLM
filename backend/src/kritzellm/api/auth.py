"""Bearer-token auth (enforced once the server has settings)."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(
    scheme_name="bearerAuth",
    description="The `API_TOKEN` configured on the server. Only needed when one is set.",
    auto_error=False,
)


async def require_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> None:
    """Checks the bearer token. Not enforced yet: there's no `API_TOKEN` setting so far."""
