"""Search over all pages."""

from enum import StrEnum

from .blocks import Block
from .common import ApiModel
from .pages import PageSummary


class SearchMode(StrEnum):
    """Which retrieval to use. `hybrid` merges `vector` and `keyword` results."""

    HYBRID = "hybrid"
    VECTOR = "vector"
    KEYWORD = "keyword"


class SearchHit(ApiModel):
    """One chunk of a page that matches the query."""

    score: float
    """Relevance score; higher is better. Only comparable within one response."""
    page: PageSummary
    blocks: list[Block]
    """The blocks this hit covers, in reading order."""
    snippet: str
    """Short excerpt around the best match."""


class SearchResults(ApiModel):
    """Search hits, best first."""

    query: str
    """The query as received."""
    mode: SearchMode
    """The retrieval mode that was used."""
    items: list[SearchHit]
