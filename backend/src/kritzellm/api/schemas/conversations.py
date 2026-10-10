"""Conversations with the journal agent, and the chat stream."""

from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field

from .blocks import Block
from .common import ApiModel, ConversationId, Cursor, InputModel, MessageId, Problem, Timestamp
from .pages import PageSummary


class Role(StrEnum):
    """Who wrote a message."""

    USER = "user"
    ASSISTANT = "assistant"


class ToolName(StrEnum):
    """Tools the agent can use."""

    SEARCH_JOURNAL = "searchJournal"
    FIND_EXACT = "findExact"
    LIST_PAGES = "listPages"
    READ_PAGE = "readPage"
    VIEW_BLOCK_IMAGE = "viewBlockImage"


class ToolCall(ApiModel):
    """One tool call the agent made."""

    name: ToolName
    arguments: dict[str, Any]
    """The arguments the agent passed."""
    summary: str
    """One-line, human-readable summary of the result."""


class Source(ApiModel):
    """A journal block cited in an answer."""

    ref: int = Field(ge=1)
    """The `n` in the `[n]` marker in the message text."""
    block: Block
    page: PageSummary
    quote: str
    """The part of the block the answer relies on."""


class Message(ApiModel):
    """A chat message."""

    id: MessageId
    conversation_id: ConversationId
    role: Role
    content: str
    """Message text (Markdown). Assistant messages cite sources as `[n]`."""
    tool_calls: list[ToolCall]
    """Tools the agent used while answering, in order. Empty for user messages."""
    sources: list[Source]
    """Journal blocks cited in `content`, one per `[n]`. Empty for user messages."""
    created_at: Timestamp


class MessageCreate(InputModel):
    """A user message."""

    content: str = Field(min_length=1, max_length=4000)
    """The user's message."""


class Conversation(ApiModel):
    """A chat thread."""

    id: ConversationId
    title: str | None = Field(max_length=200)
    """Thread title; `null` until one is set or generated."""
    message_count: int = Field(ge=0)
    """Number of messages in the thread."""
    created_at: Timestamp
    updated_at: Timestamp


class ConversationDetail(Conversation):
    """A chat thread with all of its messages."""

    messages: list[Message]
    """All messages, oldest first."""


class ConversationCreate(InputModel):
    """A new chat thread."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    """Optional title; generated from the first message when omitted."""


class ConversationUpdate(InputModel):
    """A new title for a chat thread."""

    title: str = Field(min_length=1, max_length=200)
    """New title."""


class ConversationList(ApiModel):
    """A page of conversations."""

    items: list[Conversation]
    next_cursor: Cursor


# --- Chat stream --------------------------------------------------------------------------


class StreamEvent(ApiModel):
    """Base for chat stream events: `type` always appears on the wire."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)


class MessageStartEvent(StreamEvent):
    """The assistant started answering."""

    type: Literal["messageStart"] = "messageStart"
    conversation_id: ConversationId
    message_id: MessageId


class ToolCallEvent(StreamEvent):
    """The agent is calling a tool, e.g. to show "Searching 'Lisbon'…"."""

    type: Literal["toolCall"] = "toolCall"
    name: ToolName
    arguments: dict[str, Any]
    """The arguments the agent passed."""


class ToolResultEvent(StreamEvent):
    """A tool call finished."""

    type: Literal["toolResult"] = "toolResult"
    name: ToolName
    summary: str
    """One-line, human-readable summary of the result."""


class TextDeltaEvent(StreamEvent):
    """The next piece of the answer. Concatenate all deltas to get the message `content`."""

    type: Literal["textDelta"] = "textDelta"
    text: str
    """Text to append."""


class SourceEvent(StreamEvent):
    """A citation was confirmed. Sent at the end, before `messageEnd`, once per source."""

    type: Literal["source"] = "source"
    source: Source


class MessageEndEvent(StreamEvent):
    """The answer is complete. Carries the stored message, exactly as the JSON mode returns it."""

    type: Literal["messageEnd"] = "messageEnd"
    message: Message


class ErrorEvent(StreamEvent):
    """Answering failed. The stream ends after this event."""

    type: Literal["error"] = "error"
    problem: Problem


ChatStreamEvent = Annotated[
    MessageStartEvent
    | ToolCallEvent
    | ToolResultEvent
    | TextDeltaEvent
    | SourceEvent
    | MessageEndEvent
    | ErrorEvent,
    Field(discriminator="type"),
]
"""One Server-Sent Event of a streamed answer. The SSE `event:` field equals `type`."""
