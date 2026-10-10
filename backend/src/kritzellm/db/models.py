"""The database tables."""

import uuid
from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    REAL,
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    MetaData,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy import text as sql
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from kritzellm.api.schemas.blocks import BlockKind, Side
from kritzellm.api.schemas.conversations import Role
from kritzellm.api.schemas.pages import PageStatus
from kritzellm.ids import Prefix, new_id, new_uuid

from .types import TypeId

EMBEDDING_DIMENSIONS = 1536
"""Native size of `text-embedding-3-small`."""


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_N_name)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
    type_annotation_map = {  # noqa: RUF012
        str: Text(),
        datetime: DateTime(timezone=True),
        dict[str, Any]: JSONB(),
        list[dict[str, Any]]: JSONB(),
    }


def _id(prefix: Prefix) -> Mapped[str]:
    return mapped_column(TypeId(prefix), primary_key=True, default=lambda: new_id(prefix))


def _enum(enum: type[StrEnum]) -> SAEnum:
    return SAEnum(
        enum,
        native_enum=False,
        values_callable=lambda members: [member.value for member in members],
    )


def _one_of(column: str, enum: type[StrEnum]) -> CheckConstraint:
    values = ", ".join(f"'{member.value}'" for member in enum)
    return CheckConstraint(f"{column} IN ({values})", name=f"{column}_valid")


class Timestamps:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class Journal(Timestamps, Base):
    __tablename__ = "journals"

    id: Mapped[str] = _id(Prefix.JOURNAL)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None]

    pages: Mapped[list[Page]] = relationship(
        back_populates="journal", lazy="raise", passive_deletes=True
    )


class Page(Timestamps, Base):
    __tablename__ = "pages"
    __table_args__ = (
        UniqueConstraint("journal_id", "sha256"),
        UniqueConstraint("journal_id", "page_number", deferrable=True, initially="DEFERRED"),
        CheckConstraint("page_number >= 1", name="page_number_positive"),
        CheckConstraint("width >= 1 AND height >= 1", name="size_positive"),
        _one_of("status", PageStatus),
    )

    id: Mapped[str] = _id(Prefix.PAGE)
    journal_id: Mapped[str] = mapped_column(
        TypeId(Prefix.JOURNAL), ForeignKey("journals.id", ondelete="CASCADE")
    )
    page_number: Mapped[int]
    page_label: Mapped[str | None] = mapped_column(String(40))
    entry_dates: Mapped[list[date]] = mapped_column(ARRAY(Date), server_default=sql("'{}'"))
    status: Mapped[PageStatus] = mapped_column(
        _enum(PageStatus), server_default=PageStatus.UPLOADED.value
    )
    error: Mapped[dict[str, Any] | None]
    """The RFC 9457 problem that made processing fail."""
    transcription_model: Mapped[str | None]

    original_filename: Mapped[str]
    original_media_type: Mapped[str]
    sha256: Mapped[bytes] = mapped_column(LargeBinary(32))
    """Hash of the uploaded file, to spot re-uploads."""
    width: Mapped[int]
    """Width of the normalized image in pixels."""
    height: Mapped[int]
    """Height of the normalized image in pixels."""

    journal: Mapped[Journal] = relationship(back_populates="pages", lazy="raise")
    blocks: Mapped[list[Block]] = relationship(
        back_populates="page", lazy="raise", passive_deletes=True, order_by="Block.seq"
    )
    chunks: Mapped[list[Chunk]] = relationship(
        back_populates="page", lazy="raise", passive_deletes=True
    )


class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (
        UniqueConstraint("page_id", "seq", deferrable=True, initially="DEFERRED"),
        CheckConstraint("seq >= 0", name="seq_not_negative"),
        CheckConstraint(
            "1 <= band_start AND band_start <= band_end AND band_end <= band_total",
            name="bands_in_order",
        ),
        CheckConstraint(
            "box_x BETWEEN 0 AND 1 AND box_y BETWEEN 0 AND 1"
            " AND box_width BETWEEN 0 AND 1 AND box_height BETWEEN 0 AND 1",
            name="box_normalized",
        ),
        _one_of("kind", BlockKind),
        _one_of("side", Side),
        Index(None, "text", postgresql_using="gin", postgresql_ops={"text": "gin_trgm_ops"}),
    )

    id: Mapped[str] = _id(Prefix.BLOCK)
    page_id: Mapped[str] = mapped_column(
        TypeId(Prefix.PAGE), ForeignKey("pages.id", ondelete="CASCADE")
    )
    seq: Mapped[int]
    """Position in reading order, from 0."""
    kind: Mapped[BlockKind] = mapped_column(_enum(BlockKind))
    text: Mapped[str]
    uncertain: Mapped[bool] = mapped_column(server_default=sql("false"))

    band_start: Mapped[int]
    band_end: Mapped[int]
    band_total: Mapped[int]
    side: Mapped[Side] = mapped_column(_enum(Side))
    box_x: Mapped[float] = mapped_column(REAL)
    box_y: Mapped[float] = mapped_column(REAL)
    box_width: Mapped[float] = mapped_column(REAL)
    box_height: Mapped[float] = mapped_column(REAL)

    page: Mapped[Page] = relationship(back_populates="blocks", lazy="raise")


class Chunk(Base):
    """A stretch of consecutive blocks on one page, embedded for search."""

    __tablename__ = "chunks"
    __table_args__ = (
        Index(
            None,
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index(None, "tsv", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    page_id: Mapped[str] = mapped_column(
        TypeId(Prefix.PAGE), ForeignKey("pages.id", ondelete="CASCADE"), index=True
    )
    block_ids: Mapped[list[str]] = mapped_column(ARRAY(TypeId(Prefix.BLOCK)))
    """The chunk's blocks, in reading order."""
    text: Mapped[str]
    embed_text: Mapped[str]
    """`text` with a context header (journal, page, date): what was embedded."""
    entry_date: Mapped[date | None]
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS))
    embed_model: Mapped[str]
    tsv: Mapped[str] = mapped_column(
        TSVECTOR, Computed("to_tsvector('simple', text)", persisted=True)
    )
    """Keyword-search index of `text`, kept up to date by Postgres."""

    page: Mapped[Page] = relationship(back_populates="chunks", lazy="raise")


class Conversation(Timestamps, Base):
    __tablename__ = "conversations"

    id: Mapped[str] = _id(Prefix.CONVERSATION)
    title: Mapped[str | None] = mapped_column(String(200))

    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation", lazy="raise", passive_deletes=True, order_by="Message.id"
    )


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (Index(None, "conversation_id", "id"), _one_of("role", Role))

    id: Mapped[str] = _id(Prefix.MESSAGE)
    """UUIDv7, so ordering by ID is ordering by time."""
    conversation_id: Mapped[str] = mapped_column(
        TypeId(Prefix.CONVERSATION), ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role: Mapped[Role] = mapped_column(_enum(Role))
    content: Mapped[str]
    tool_calls: Mapped[list[dict[str, Any]]] = mapped_column(server_default=sql("'[]'"))
    """The API's `ToolCall`s, in order."""
    sources: Mapped[list[dict[str, Any]]] = mapped_column(server_default=sql("'[]'"))
    """The API's `Source`s, as they were when the answer was given."""
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    conversation: Mapped[Conversation] = relationship(back_populates="messages", lazy="raise")
