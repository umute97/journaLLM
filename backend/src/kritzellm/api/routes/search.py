from typing import Annotated

from fastapi import APIRouter, Query

from ..errors import not_implemented, problem_responses
from ..schemas.common import JournalId
from ..schemas.search import SearchMode, SearchResults
from .params import DateFrom, DateTo

router = APIRouter(tags=["search"])


@router.get(
    "/search",
    summary="Search the journal",
    responses=problem_responses(400, 401, 422),
)
async def search(
    q: Annotated[
        str, Query(min_length=1, max_length=500, description="What to look for, in plain words.")
    ],
    mode: Annotated[SearchMode, Query(description="Which retrieval to use.")] = SearchMode.HYBRID,
    journal_id: Annotated[
        JournalId | None, Query(alias="journalId", description="Only search this journal.")
    ] = None,
    date_from: DateFrom = None,
    date_to: DateTo = None,
    limit: Annotated[int, Query(ge=1, le=50, description="Maximum number of hits.")] = 10,
) -> SearchResults:
    """Finds passages by meaning and by exact words.

    `hybrid` (the default) merges vector and full-text results with reciprocal rank fusion;
    `vector` and `keyword` return either side on its own, which helps when tuning. Each hit is one
    chunk of a page, with the blocks it covers.
    """
    not_implemented()
