"""Journals: notebooks (or volumes) that pages belong to."""

from enum import StrEnum

from pydantic import Field

from .common import ApiModel, Cursor, InputModel, JournalId, Timestamp


class Journal(ApiModel):
    """A notebook (or volume) of handwritten pages."""

    id: JournalId
    name: str = Field(min_length=1, max_length=120)
    """Display name."""
    description: str | None = Field(max_length=2000)
    """Optional notes about the journal."""
    page_count: int = Field(ge=0)
    """Number of pages in the journal."""
    created_at: Timestamp
    updated_at: Timestamp


class JournalCreate(InputModel):
    """A new journal."""

    name: str = Field(min_length=1, max_length=120)
    """Display name."""
    description: str | None = Field(default=None, max_length=2000)
    """Optional notes about the journal."""


class JournalUpdate(InputModel):
    """Changes to a journal. Only the given fields change."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    """New display name."""
    description: str | None = Field(default=None, max_length=2000)
    """New notes; `null` clears them."""


class JournalList(ApiModel):
    """A page of journals."""

    items: list[Journal]
    next_cursor: Cursor


class ExportFormat(StrEnum):
    """`markdown`: one file per page plus images. `json`: everything machine-readable. Both come zipped."""

    MARKDOWN = "markdown"
    JSON = "json"


class ExportCreate(InputModel):
    """Options for a journal export."""

    format: ExportFormat
