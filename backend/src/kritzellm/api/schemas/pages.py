"""Pages: uploaded page images and their transcriptions."""

from enum import StrEnum

from pydantic import Field

from .blocks import Block
from .common import ApiModel, Cursor, Day, InputModel, JournalId, PageId, Problem, Timestamp
from .jobs import Job


class PageStatus(StrEnum):
    """Where a page is in processing.

    `uploaded` (waiting for the worker) → `transcribing` → `indexing` → `ready`.
    `failed` means a step failed; see `error` and re-transcribe to retry.
    """

    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    INDEXING = "indexing"
    READY = "ready"
    FAILED = "failed"


class ImageVariant(StrEnum):
    """Which version of a page image to return."""

    NORMALIZED = "normalized"
    ORIGINAL = "original"
    THUMBNAIL = "thumbnail"


class PageImageUrls(ApiModel):
    """Where to fetch each version of a page image."""

    normalized: str
    """The rotated, resized image all block locations refer to."""
    original: str
    """The uploaded file as-is."""
    thumbnail: str
    """A small preview."""


class PageImage(ApiModel):
    """A page's image."""

    width: int = Field(ge=1)
    """Width of the normalized image in pixels."""
    height: int = Field(ge=1)
    """Height of the normalized image in pixels."""
    urls: PageImageUrls


class Page(ApiModel):
    """An uploaded page."""

    id: PageId
    journal_id: JournalId
    page_number: int = Field(ge=1)
    """Position of the page in its journal."""
    page_label: str | None = Field(max_length=40)
    """Page number or label as written on the page itself, if any."""
    entry_dates: list[Day]
    """Dates of the entries on this page, as read from the page or set by hand."""
    status: PageStatus
    error: Problem | None
    """Why processing failed; `null` unless `status` is `failed`."""
    image: PageImage
    transcription_model: str | None
    """Model that produced the current transcription; `null` until transcribed."""
    created_at: Timestamp
    updated_at: Timestamp


class PageDetail(Page):
    """A page with its transcribed blocks."""

    blocks: list[Block]
    """Transcribed blocks in reading order."""


class PageSummary(ApiModel):
    """The bits of a page needed to show where something came from."""

    id: PageId
    journal_id: JournalId
    journal_name: str
    """Name of the page's journal."""
    page_number: int = Field(ge=1)
    """Position of the page in its journal."""
    page_label: str | None
    """Page number or label as written on the page itself, if any."""
    entry_dates: list[Day]
    """Dates of the entries on this page."""
    thumbnail_url: str
    """Small preview image."""


class PageUpdate(InputModel):
    """Corrections to a page's metadata. Only the given fields change."""

    journal_id: JournalId | None = None
    """Move the page to this journal."""
    page_number: int | None = Field(default=None, ge=1)
    """New position in the journal. Must not be taken by another page."""
    page_label: str | None = Field(default=None, max_length=40)
    """Label as written on the page; `null` clears it."""
    entry_dates: list[Day] | None = None
    """Corrected entry dates."""


class PageList(ApiModel):
    """A page of pages."""

    items: list[Page]
    next_cursor: Cursor


class UploadItem(ApiModel):
    """The outcome for one uploaded file."""

    filename: str
    """The uploaded file's name."""
    page: Page
    duplicate: bool
    """`true` if this exact file was already in the journal; `page` is then the existing page."""
    job: Job | None
    """The processing job for a new page; `null` for duplicates."""


class UploadResult(ApiModel):
    """One entry per uploaded file, in upload order."""

    items: list[UploadItem]


class TranscribeRequest(InputModel):
    """Options for re-transcribing a page."""

    model: str | None = Field(default=None, min_length=1)
    """Vision model to use instead of the configured one."""
