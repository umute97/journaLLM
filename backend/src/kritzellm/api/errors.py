"""RFC 9457 problem details for every error the API returns."""

from http import HTTPStatus
from typing import Any, NoReturn

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .schemas.common import Problem, ProblemError

PROBLEM_JSON = "application/problem+json"

_DESCRIPTIONS = {
    400: "The request couldn't be parsed (e.g. malformed JSON or multipart).",
    401: "Missing or wrong bearer token.",
    404: "The resource doesn't exist.",
    406: "The `Accept` header asks for a format this endpoint can't produce.",
    409: "The request conflicts with the current state (e.g. a job is still running).",
    413: "An uploaded file is too big.",
    415: "An uploaded file isn't a supported image type.",
    422: "Some values are invalid (including malformed IDs). Each one is listed in `errors`.",
}


def problem_responses(*statuses: int) -> dict[int | str, dict[str, Any]]:
    """OpenAPI `responses` entries for the given error statuses."""
    return {status: {"model": Problem, "description": _DESCRIPTIONS[status]} for status in statuses}


class ProblemResponse(JSONResponse):
    media_type = PROBLEM_JSON


def problem(
    status: int,
    detail: str | None = None,
    *,
    request: Request | None = None,
    errors: list[ProblemError] | None = None,
) -> ProblemResponse:
    body = Problem(
        title=HTTPStatus(status).phrase,
        status=status,
        detail=detail,
        instance=request.url.path if request else None,
        errors=errors,
    )
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    return ProblemResponse(
        body.model_dump(mode="json", exclude_none=True), status_code=status, headers=headers
    )


class NotImplementedYetError(Exception):
    """Raised by routes whose behaviour hasn't been built yet."""


def not_implemented() -> NoReturn:
    raise NotImplementedYetError


def _validation_errors(exc: RequestValidationError) -> list[ProblemError]:
    errors = []
    for error in exc.errors():
        where, *path = error["loc"] or ("body",)
        message = error["msg"]
        if where == "body":
            pointer = "/" + "/".join(str(part) for part in path)
            errors.append(ProblemError(detail=message, pointer=pointer))
        else:
            errors.append(ProblemError(detail=message, parameter=str(path[0]) if path else None))
    return errors


def install_problem_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException) -> ProblemResponse:
        detail = exc.detail if isinstance(exc.detail, str) else None
        return problem(exc.status_code, detail, request=request)

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> ProblemResponse:
        if any(error["type"] == "json_invalid" for error in exc.errors()):
            return problem(400, "The request body is not valid JSON.", request=request)
        errors = _validation_errors(exc)
        detail = f"The request has {len(errors)} invalid value{'s' if len(errors) != 1 else ''}."
        return problem(422, detail, request=request, errors=errors)

    @app.exception_handler(NotImplementedYetError)
    async def _not_implemented(request: Request, exc: NotImplementedYetError) -> ProblemResponse:
        return problem(501, "This endpoint is designed but not built yet.", request=request)
