"""Blocks: located pieces of text on a page (paragraphs, lists, margin notes, ...)."""

from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from .common import ApiModel, BlockId, InputModel, PageId
from .jobs import Job


class BlockKind(StrEnum):
    """What kind of thing a block is on the page. Drawings are described in words, in brackets."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    MARGIN_NOTE = "marginNote"
    DRAWING = "drawing"
    OTHER = "other"


class Side(StrEnum):
    """Horizontal placement. `full` spans the text width; `left`/`right` are margin notes or columns."""

    LEFT = "left"
    RIGHT = "right"
    FULL = "full"


class Bands(ApiModel):
    """A block's vertical extent in ruler bands.

    While transcribing, the page is split into `total` equal horizontal bands numbered from 1 at
    the top; the block covers bands `start` to `end`.
    """

    start: int = Field(ge=1)
    """First band the block touches."""
    end: int = Field(ge=1)
    """Last band the block touches (≥ `start`)."""
    total: int = Field(ge=1)
    """How many bands the page was split into."""


class BandRange(InputModel):
    """A block's vertical extent in the page's ruler bands (see `Bands`)."""

    start: int = Field(ge=1)
    """First band the block touches."""
    end: int = Field(ge=1)
    """Last band the block touches (≥ `start`)."""

    @model_validator(mode="after")
    def _end_after_start(self) -> Self:
        if self.end < self.start:
            raise ValueError("`end` must be ≥ `start`")
        return self


class Box(ApiModel):
    """A rectangle in normalized page coordinates (`0,0` top-left, `1,1` bottom-right)."""

    x: float = Field(ge=0, le=1)
    """Left edge."""
    y: float = Field(ge=0, le=1)
    """Top edge."""
    width: float = Field(ge=0, le=1)
    """Width."""
    height: float = Field(ge=0, le=1)
    """Height."""


class Location(ApiModel):
    """Where a block sits on its page."""

    box: Box
    bands: Bands
    side: Side
    label: str
    """Human-friendly description of the spot, e.g. "middle of the page, paragraph 3"."""


class Block(ApiModel):
    """A located piece of text on a page."""

    id: BlockId
    page_id: PageId
    seq: int = Field(ge=0)
    """Position in reading order, starting at 0."""
    kind: BlockKind
    text: str
    """The transcribed text. Unreadable words are written as `[?]`."""
    uncertain: bool
    """`true` when the model wasn't sure about parts of this block."""
    location: Location


class BlockInput(InputModel):
    """One block in a full replacement of a page's blocks."""

    id: BlockId | None = None
    """Set to update an existing block in place; omit to create a new one."""
    kind: BlockKind
    text: str = Field(min_length=1, max_length=20_000)
    """The block's text."""
    uncertain: bool = False
    """Whether parts of the text are still unsure."""
    bands: BandRange
    side: Side


class BlocksReplace(InputModel):
    """All blocks of a page, in reading order."""

    blocks: list[BlockInput] = Field(max_length=500)


class BlocksReplaceResult(ApiModel):
    """A page's blocks after a replacement, plus the re-index job."""

    blocks: list[Block]
    """The page's blocks after the change, in reading order."""
    job: Job


class BlockUpdate(InputModel):
    """Corrections to a single block. Only the given fields change."""

    kind: BlockKind | None = None
    text: str | None = Field(default=None, min_length=1, max_length=20_000)
    """Corrected text."""
    uncertain: bool | None = None
    """Whether parts of the text are still unsure."""


class BlockUpdateResult(ApiModel):
    """The corrected block, plus the re-index job."""

    block: Block
    job: Job
