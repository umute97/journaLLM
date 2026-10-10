"""Bearer-token auth, enforced when the server has an `API_TOKEN`."""

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from kritzellm.config import Settings

from .deps import get_settings

bearer = HTTPBearer(
    scheme_name="bearerAuth",
    description="The `API_TOKEN` configured on the server. Only needed when one is set.",
    auto_error=False,
)


async def require_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """Rejects the request with a `401` unless it carries the configured token."""
    if settings.api_token is None:
        return
    expected = settings.api_token.get_secret_value().encode()
    given = credentials.credentials.encode() if credentials else b""
    if not secrets.compare_digest(given, expected):
        raise HTTPException(401, "Missing or wrong bearer token.")
