from typing import Annotated

from fastapi import APIRouter, Body, Query, Response, status

from ..errors import not_implemented, problem_responses
from ..schemas.blocks import BlocksReplace, BlocksReplaceResult
from ..schemas.common import JournalId
from ..schemas.jobs import Job
from ..schemas.pages import (
    ImageVariant,
    Page,
    PageDetail,
    PageList,
    PageStatus,
    PageUpdate,
    TranscribeRequest,
)
from .params import BINARY, JOB_LOCATION, CursorQuery, DateFrom, DateTo, Limit, PageIdPath

router = APIRouter(tags=["pages"])


@router.get(
    "/pages",
    summary="List pages",
    responses=problem_responses(400, 401, 422),
)
async def list_pages(
    journal_id: Annotated[
        JournalId | None, Query(alias="journalId", description="Only pages of this journal.")
    ] = None,
    page_status: Annotated[
        PageStatus | None, Query(alias="status", description="Only pages in this status.")
    ] = None,
    date_from: DateFrom = None,
    date_to: DateTo = None,
    limit: Limit = 25,
    cursor: CursorQuery = None,
) -> PageList:
    """Lists pages, ordered by journal and page number."""
    not_implemented()


@router.get(
    "/pages/{pageId}",
    summary="Get a page",
    responses=problem_responses(400, 401, 404, 422),
)
async def get_page(page_id: PageIdPath) -> PageDetail:
    """Returns a page with all of its transcribed blocks, in reading order."""
    not_implemented()


@router.patch(
    "/pages/{pageId}",
    summary="Update a page",
    responses=problem_responses(400, 401, 404, 409, 422),
)
async def update_page(page_id: PageIdPath, body: PageUpdate) -> Page:
    """Corrects page metadata (number, label, dates) or moves the page to another journal.

    Changing dates or the journal re-indexes the page.
    """
    not_implemented()


@router.delete(
    "/pages/{pageId}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a page",
    responses=problem_responses(400, 401, 404, 422),
)
async def delete_page(page_id: PageIdPath) -> None:
    """Deletes a page, its images, blocks and search index entries. This can't be undone."""
    not_implemented()


@router.get(
    "/pages/{pageId}/image",
    response_class=Response,
    summary="Get a page image",
    responses={
        200: {
            "description": "The image bytes.",
            "content": {
                "image/jpeg": BINARY,
                "image/png": BINARY,
                "image/heic": BINARY,
                "image/heif": BINARY,
                "image/webp": BINARY,
            },
        },
        **problem_responses(400, 401, 404, 422),
    },
)
async def get_page_image(
    page_id: PageIdPath,
    variant: Annotated[
        ImageVariant, Query(description="Which version of the image to return.")
    ] = ImageVariant.NORMALIZED,
) -> Response:
    """Returns the page image.

    `normalized` (the default) is the rotated, resized JPEG that all block locations refer to.
    `original` is the uploaded file as-is, and `thumbnail` is a small JPEG preview.
    """
    not_implemented()


@router.put(
    "/pages/{pageId}/blocks",
    summary="Replace a page's blocks",
    tags=["blocks"],
    responses=problem_responses(400, 401, 404, 409, 422),
)
async def replace_page_blocks(page_id: PageIdPath, body: BlocksReplace) -> BlocksReplaceResult:
    """Replaces the whole transcription of a page, in reading order.

    Blocks sent with an `id` are updated in place (so existing chat sources keep working); blocks
    without one are created; existing blocks that aren't sent are deleted. The page is re-indexed in
    the background.
    """
    not_implemented()


@router.post(
    "/pages/{pageId}/transcribe",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Re-transcribe a page",
    responses={202: {"headers": JOB_LOCATION}, **problem_responses(400, 401, 404, 409, 422)},
)
async def transcribe_page(
    page_id: PageIdPath, body: Annotated[TranscribeRequest | None, Body()] = None
) -> Job:
    """Throws away the current blocks and reads the page again, optionally with another model.

    Manual edits are lost.
    """
    not_implemented()
