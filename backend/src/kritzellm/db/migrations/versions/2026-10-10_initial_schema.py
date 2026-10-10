"""initial schema

Created: 2026-10-10 16:09:30.495859
"""

from collections.abc import Sequence

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0848061d24cd"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversations")),
    )
    op.create_table(
        "journals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_journals")),
    )
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role", sa.Enum("user", "assistant", name="role", native_enum=False), nullable=False
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "tool_calls",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "sources",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("role IN ('user', 'assistant')", name=op.f("ck_messages_role_valid")),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name=op.f("fk_messages_conversation_id_conversations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_messages")),
    )
    op.create_index(
        op.f("ix_messages_conversation_id_id"), "messages", ["conversation_id", "id"], unique=False
    )
    op.create_table(
        "pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("journal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("page_label", sa.String(length=40), nullable=True),
        sa.Column(
            "entry_dates",
            postgresql.ARRAY(sa.Date()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "uploaded",
                "transcribing",
                "indexing",
                "ready",
                "failed",
                name="pagestatus",
                native_enum=False,
            ),
            server_default="uploaded",
            nullable=False,
        ),
        sa.Column("error", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("transcription_model", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.Text(), nullable=False),
        sa.Column("original_media_type", sa.Text(), nullable=False),
        sa.Column("sha256", sa.LargeBinary(length=32), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('uploaded', 'transcribing', 'indexing', 'ready', 'failed')",
            name=op.f("ck_pages_status_valid"),
        ),
        sa.CheckConstraint("page_number >= 1", name=op.f("ck_pages_page_number_positive")),
        sa.CheckConstraint("width >= 1 AND height >= 1", name=op.f("ck_pages_size_positive")),
        sa.ForeignKeyConstraint(
            ["journal_id"],
            ["journals.id"],
            name=op.f("fk_pages_journal_id_journals"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pages")),
        sa.UniqueConstraint(
            "journal_id",
            "page_number",
            deferrable=True,
            initially="DEFERRED",
            name=op.f("uq_pages_journal_id_page_number"),
        ),
        sa.UniqueConstraint("journal_id", "sha256", name=op.f("uq_pages_journal_id_sha256")),
    )
    op.create_table(
        "blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "heading",
                "paragraph",
                "list",
                "marginNote",
                "drawing",
                "other",
                name="blockkind",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("uncertain", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("band_start", sa.Integer(), nullable=False),
        sa.Column("band_end", sa.Integer(), nullable=False),
        sa.Column("band_total", sa.Integer(), nullable=False),
        sa.Column(
            "side", sa.Enum("left", "right", "full", name="side", native_enum=False), nullable=False
        ),
        sa.Column("box_x", sa.REAL(), nullable=False),
        sa.Column("box_y", sa.REAL(), nullable=False),
        sa.Column("box_width", sa.REAL(), nullable=False),
        sa.Column("box_height", sa.REAL(), nullable=False),
        sa.CheckConstraint(
            "kind IN ('heading', 'paragraph', 'list', 'marginNote', 'drawing', 'other')",
            name=op.f("ck_blocks_kind_valid"),
        ),
        sa.CheckConstraint("side IN ('left', 'right', 'full')", name=op.f("ck_blocks_side_valid")),
        sa.CheckConstraint(
            "1 <= band_start AND band_start <= band_end AND band_end <= band_total",
            name=op.f("ck_blocks_bands_in_order"),
        ),
        sa.CheckConstraint(
            "box_x BETWEEN 0 AND 1 AND box_y BETWEEN 0 AND 1 AND box_width BETWEEN 0 AND 1 AND box_height BETWEEN 0 AND 1",
            name=op.f("ck_blocks_box_normalized"),
        ),
        sa.CheckConstraint("seq >= 0", name=op.f("ck_blocks_seq_not_negative")),
        sa.ForeignKeyConstraint(
            ["page_id"], ["pages.id"], name=op.f("fk_blocks_page_id_pages"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_blocks")),
        sa.UniqueConstraint(
            "page_id",
            "seq",
            deferrable=True,
            initially="DEFERRED",
            name=op.f("uq_blocks_page_id_seq"),
        ),
    )
    op.create_index(
        op.f("ix_blocks_text"),
        "blocks",
        ["text"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"text": "gin_trgm_ops"},
    )
    op.create_table(
        "chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("block_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embed_text", sa.Text(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=True),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(1536), nullable=False),
        sa.Column("embed_model", sa.Text(), nullable=False),
        sa.Column(
            "tsv",
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('simple', text)", persisted=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["page_id"], ["pages.id"], name=op.f("fk_chunks_page_id_pages"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chunks")),
    )
    op.create_index(
        op.f("ix_chunks_embedding"),
        "chunks",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.create_index(op.f("ix_chunks_page_id"), "chunks", ["page_id"], unique=False)
    op.create_index(op.f("ix_chunks_tsv"), "chunks", ["tsv"], unique=False, postgresql_using="gin")


def downgrade() -> None:
    # Leaves the extensions in place; other database objects may use them.
    op.drop_index(op.f("ix_chunks_tsv"), table_name="chunks", postgresql_using="gin")
    op.drop_index(op.f("ix_chunks_page_id"), table_name="chunks")
    op.drop_index(
        op.f("ix_chunks_embedding"),
        table_name="chunks",
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.drop_table("chunks")
    op.drop_index(
        op.f("ix_blocks_text"),
        table_name="blocks",
        postgresql_using="gin",
        postgresql_ops={"text": "gin_trgm_ops"},
    )
    op.drop_table("blocks")
    op.drop_table("pages")
    op.drop_index(op.f("ix_messages_conversation_id_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_table("journals")
    op.drop_table("conversations")
