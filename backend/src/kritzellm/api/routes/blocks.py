from typing import Annotated

from fastapi import APIRouter, Query, Response

from ..errors import not_implemented, problem_responses
from ..schemas.blocks import Block, BlockUpdate, BlockUpdateResult
from .params import BINARY, BlockIdPath

router = APIRouter(tags=["blocks"])


@router.get(
    "/blocks/{blockId}",
    summary="Get a block",
    responses=problem_responses(400, 401, 404, 422),
)
async def get_block(block_id: BlockIdPath) -> Block:
    """Returns a single block. Handy for resolving a chat source."""
    not_implemented()


@router.patch(
    "/blocks/{blockId}",
    summary="Fix a block",
    responses=problem_responses(400, 401, 404, 422),
)
async def update_block(block_id: BlockIdPath, body: BlockUpdate) -> BlockUpdateResult:
    """Corrects a block's text, kind or `uncertain` flag. Its page is re-indexed in the background."""
    not_implemented()


@router.get(
    "/blocks/{blockId}/image",
    response_class=Response,
    summary="Get a block's image crop",
    responses={
        200: {"description": "A JPEG crop of the block.", "content": {"image/jpeg": BINARY}},
        **problem_responses(400, 401, 404, 422),
    },
)
async def get_block_image(
    block_id: BlockIdPath,
    padding: Annotated[
        float,
        Query(
            ge=0,
            le=0.25,
            description="Extra margin around the block, as a fraction of the page height.",
        ),
    ] = 0.02,
) -> Response:
    """Returns the part of the normalized page image that the block covers, plus a little padding."""
    not_implemented()
