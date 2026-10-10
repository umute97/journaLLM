from typing import Annotated

from fastapi import APIRouter, File, Form, Header, Response, UploadFile, status

from ..errors import not_implemented, problem_responses
from ..schemas.jobs import Job
from ..schemas.journals import ExportCreate, Journal, JournalCreate, JournalList, JournalUpdate
from ..schemas.pages import UploadResult
from .params import JOB_LOCATION, CursorQuery, JournalIdPath, Limit, location_header

router = APIRouter(tags=["journals"])


@router.get(
    "/journals",
    summary="List journals",
    responses=problem_responses(400, 401, 422),
)
async def list_journals(limit: Limit = 25, cursor: CursorQuery = None) -> JournalList:
    """Lists all journals, newest first."""
    not_implemented()


@router.post(
    "/journals",
    status_code=status.HTTP_201_CREATED,
    summary="Create a journal",
    responses={
        201: {"headers": location_header("URL of the new journal.")},
        **problem_responses(400, 401, 422),
    },
)
async def create_journal(body: JournalCreate) -> Journal:
    """Creates an empty journal to upload pages into."""
    not_implemented()


@router.get(
    "/journals/{journalId}",
    summary="Get a journal",
    responses=problem_responses(400, 401, 404, 422),
)
async def get_journal(journal_id: JournalIdPath) -> Journal:
    """Returns a single journal."""
    not_implemented()


@router.patch(
    "/journals/{journalId}",
    summary="Update a journal",
    responses=problem_responses(400, 401, 404, 422),
)
async def update_journal(journal_id: JournalIdPath, body: JournalUpdate) -> Journal:
    """Renames a journal or changes its description. Only the given fields change."""
    not_implemented()


@router.delete(
    "/journals/{journalId}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a journal",
    responses=problem_responses(400, 401, 404, 422),
)
async def delete_journal(journal_id: JournalIdPath) -> None:
    """Deletes a journal with all of its pages, images, blocks and search index entries.

    This can't be undone.
    """
    not_implemented()


@router.post(
    "/journals/{journalId}/pages",
    status_code=status.HTTP_201_CREATED,
    summary="Upload pages",
    tags=["pages"],
    responses=problem_responses(400, 401, 404, 413, 415, 422),
)
async def upload_pages(
    journal_id: JournalIdPath,
    files: Annotated[
        list[UploadFile],
        File(
            description="Page images in page order. JPEG, PNG, HEIC/HEIF or WebP, up to 25 MB each.",
        ),
    ],
    start_page_number: Annotated[
        int | None,
        Form(
            alias="startPageNumber",
            ge=1,
            description=(
                "Page number for the first file; the rest count up from it. "
                "Defaults to the journal's next free page number."
            ),
        ),
    ] = None,
    idempotency_key: Annotated[
        str | None,
        Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=255,
            description="Any unique string (e.g. a UUID). Retries with the same key return the first response.",
        ),
    ] = None,
) -> UploadResult:
    """Uploads page photos or scans into a journal.

    Each new page gets an `ingestPage` job that normalizes the image, transcribes it and indexes it.

    Uploads are idempotent per file: a file whose SHA-256 already exists in this journal returns the
    existing page with `duplicate: true` and no new job. Sending the same `Idempotency-Key` again
    replays the original response.
    """
    not_implemented()


@router.post(
    "/journals/{journalId}/exports",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Export a journal",
    responses={202: {"headers": JOB_LOCATION}, **problem_responses(400, 401, 404, 422)},
)
async def export_journal(journal_id: JournalIdPath, body: ExportCreate) -> Job:
    """Starts a zipped export of all pages and transcriptions.

    When the job succeeds, download the file from its `resultUrl`.
    """
    not_implemented()
