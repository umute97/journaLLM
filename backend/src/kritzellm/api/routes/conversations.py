from typing import Annotated

from fastapi import APIRouter, Body, Response, status

from ..errors import not_implemented, problem_responses
from ..schemas.conversations import (
    Conversation,
    ConversationCreate,
    ConversationDetail,
    ConversationList,
    ConversationUpdate,
    Message,
    MessageCreate,
)
from .params import ConversationIdPath, CursorQuery, Limit, location_header

router = APIRouter(tags=["conversations"])


@router.get(
    "/conversations",
    summary="List conversations",
    responses=problem_responses(400, 401, 422),
)
async def list_conversations(limit: Limit = 25, cursor: CursorQuery = None) -> ConversationList:
    """Lists chat threads, most recently active first."""
    not_implemented()


@router.post(
    "/conversations",
    status_code=status.HTTP_201_CREATED,
    summary="Start a conversation",
    responses={
        201: {"headers": location_header("URL of the new conversation.")},
        **problem_responses(400, 401, 422),
    },
)
async def create_conversation(
    body: Annotated[ConversationCreate | None, Body()] = None,
) -> Conversation:
    """Creates an empty chat thread. Without a title, one is generated from the first message."""
    not_implemented()


@router.get(
    "/conversations/{conversationId}",
    summary="Get a conversation",
    responses=problem_responses(400, 401, 404, 422),
)
async def get_conversation(conversation_id: ConversationIdPath) -> ConversationDetail:
    """Returns a chat thread with all of its messages, oldest first."""
    not_implemented()


@router.patch(
    "/conversations/{conversationId}",
    summary="Rename a conversation",
    responses=problem_responses(400, 401, 404, 422),
)
async def update_conversation(
    conversation_id: ConversationIdPath, body: ConversationUpdate
) -> Conversation:
    """Changes a conversation's title."""
    not_implemented()


@router.delete(
    "/conversations/{conversationId}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a conversation",
    responses=problem_responses(400, 401, 404, 422),
)
async def delete_conversation(conversation_id: ConversationIdPath) -> None:
    """Deletes a chat thread and its messages. Journal pages are not affected."""
    not_implemented()


@router.post(
    "/conversations/{conversationId}/messages",
    summary="Send a message",
    responses={
        200: {
            "description": "The assistant's answer, as JSON or as Server-Sent Events depending on `Accept`.",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "description": (
                            "A stream of Server-Sent Events. Each event's `data:` is one JSON "
                            "`ChatStreamEvent`."
                        ),
                        "x-event-schema": {"$ref": "#/components/schemas/ChatStreamEvent"},
                    }
                }
            },
        },
        **problem_responses(400, 401, 404, 406, 409, 422),
    },
)
async def send_message(conversation_id: ConversationIdPath, body: MessageCreate) -> Message:
    """Sends a user message and gets the agent's answer.

    The answer cites journal blocks as `[1]`, `[2]`, …, matching the `ref` of each entry in
    `sources`. Only blocks the agent actually retrieved can be cited.

    Pick the response style with the `Accept` header:

    - `application/json` waits and returns the finished assistant `Message`.
    - `text/event-stream` streams the answer as Server-Sent Events. Each event's `event:` field is
      the `type` of a `ChatStreamEvent`, and its `data:` field is that event as JSON. The stream
      always ends with `messageEnd` (carrying the same `Message` as the JSON mode) or `error`.
    """
    not_implemented()
