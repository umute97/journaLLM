"""Background jobs."""

from enum import StrEnum

from pydantic import Field

from .common import ApiModel, Cursor, JobId, Problem, Timestamp


class JobKind(StrEnum):
    """What a job does."""

    INGEST_PAGE = "ingestPage"
    TRANSCRIBE_PAGE = "transcribePage"
    REINDEX_PAGE = "reindexPage"
    REINDEX_ALL = "reindexAll"
    EXPORT_JOURNAL = "exportJournal"


class JobStatus(StrEnum):
    """Lifecycle of a job."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobTargetType(StrEnum):
    """Kind of thing a job works on."""

    PAGE = "page"
    JOURNAL = "journal"
    ALL = "all"


class JobTarget(ApiModel):
    """What the job works on."""

    type: JobTargetType
    id: str | None
    """ID of the page or journal; `null` for `all`."""


class JobProgress(ApiModel):
    """How far along a job is."""

    done: int = Field(ge=0)
    """Units finished so far."""
    total: int = Field(ge=0)
    """Total units of work."""


class Job(ApiModel):
    """A unit of background work. Poll it until `status` is `succeeded` or `failed`."""

    id: JobId
    kind: JobKind
    status: JobStatus
    target: JobTarget
    progress: JobProgress | None
    """How far along the job is, when it can tell."""
    result_url: str | None
    """Where to download the result once `succeeded` (exports only)."""
    error: Problem | None
    """Why the job failed; `null` unless `status` is `failed`."""
    created_at: Timestamp
    started_at: Timestamp | None
    """When a worker picked the job up."""
    finished_at: Timestamp | None
    """When the job succeeded or failed."""


class JobList(ApiModel):
    """A page of jobs."""

    items: list[Job]
    next_cursor: Cursor
