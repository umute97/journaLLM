"""Building blocks shared by all API schemas."""

from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """Base for everything the API sends: camelCase on the wire, snake_case in Python."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
        use_attribute_docstrings=True,
    )


class InputModel(ApiModel):
    """Base for request bodies: unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid")


def _type_id(prefix: str, what: str) -> object:
    return Annotated[
        str,
        StringConstraints(pattern=rf"^{prefix}_[0-7][0-9a-hjkmnp-tv-z]{{25}}$"),
        Field(description=f"TypeID of a {what}."),
    ]


JournalId = _type_id("jrn", "journal")
PageId = _type_id("pg", "page")
BlockId = _type_id("blk", "block")
ConversationId = _type_id("cnv", "conversation")
MessageId = _type_id("msg", "message")
JobId = _type_id("job", "job")

Timestamp = Annotated[datetime, Field(description="RFC 3339 timestamp in UTC.")]
Day = Annotated[date, Field(description="A calendar day.")]
Cursor = Annotated[
    str | None,
    Field(description="Pass as `cursor` to get the next page; `null` on the last page."),
]


class ProblemError(ApiModel):
    """One invalid value in a request."""

    detail: str
    """What's wrong with this value."""
    pointer: str | None = None
    """JSON Pointer to the offending value in the request body, e.g. `/name`."""
    parameter: str | None = None
    """Name of the offending query, path or header parameter."""


class Problem(ApiModel):
    """An RFC 9457 problem details object."""

    type: str = "about:blank"
    """Identifies the problem type; `about:blank` when there's nothing more specific."""
    title: str
    """Short, human-readable summary of the problem type."""
    status: int = Field(ge=400, le=599)
    """The HTTP status code."""
    detail: str | None = None
    """What went wrong in this particular case."""
    instance: str | None = None
    """The request path that caused the problem."""
    errors: list[ProblemError] | None = None
    """Individual validation problems (only for `422`)."""
