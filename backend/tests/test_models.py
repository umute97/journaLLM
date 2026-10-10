import hashlib
from datetime import date

import pytest
from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.ext.asyncio import AsyncSession

from kritzellm.api.schemas.blocks import BlockKind, Side
from kritzellm.api.schemas.conversations import Role
from kritzellm.api.schemas.pages import PageStatus
from kritzellm.db.models import (
    EMBEDDING_DIMENSIONS,
    Block,
    Chunk,
    Conversation,
    Journal,
    Message,
    Page,
)
from kritzellm.ids import Prefix, decode, new_id

pytestmark = [pytest.mark.db, pytest.mark.anyio]


def _page(journal: Journal, number: int, content: bytes | None = None) -> Page:
    return Page(
        journal=journal,
        page_number=number,
        original_filename=f"page-{number}.jpg",
        original_media_type="image/jpeg",
        sha256=hashlib.sha256(content or f"page {number}".encode()).digest(),
        width=1536,
        height=2048,
    )


def _block(page: Page, seq: int, text: str) -> Block:
    return Block(
        page=page,
        seq=seq,
        kind=BlockKind.PARAGRAPH,
        text=text,
        band_start=seq + 1,
        band_end=seq + 2,
        band_total=24,
        side=Side.FULL,
        box_x=0.1,
        box_y=0.05 * seq,
        box_width=0.8,
        box_height=0.08,
    )


def _embedding(hot: int) -> list[float]:
    return [1.0 if i == hot else 0.0 for i in range(EMBEDDING_DIMENSIONS)]


async def _journal_with_a_chunk(session: AsyncSession) -> tuple[Journal, Page, Chunk]:
    journal = Journal(name="Summer 2026")
    page = _page(journal, 1)
    blocks = [_block(page, 0, "Flew to Lisbon today."), _block(page, 1, "Pastéis de nata!")]
    session.add_all([journal, page, *blocks])
    await session.flush()
    chunk = Chunk(
        page=page,
        block_ids=[block.id for block in blocks],
        text="Flew to Lisbon today. Pastéis de nata!",
        embed_text="Summer 2026, page 1, 2026-07-14\n\nFlew to Lisbon today. Pastéis de nata!",
        entry_date=date(2026, 7, 14),
        embedding=_embedding(7),
        embed_model="text-embedding-3-small",
    )
    session.add(chunk)
    await session.commit()
    return journal, page, chunk


async def test_rows_round_trip_with_typeids(session: AsyncSession) -> None:
    journal, page, chunk = await _journal_with_a_chunk(session)
    session.expunge_all()

    stored = await session.scalar(select(Page).where(Page.id == page.id))
    assert stored is not None
    assert stored.id.startswith("pg_")
    assert decode(Prefix.PAGE, stored.id).version == 7
    assert stored.journal_id == journal.id
    assert stored.status is PageStatus.UPLOADED
    assert stored.entry_dates == []
    assert stored.created_at.tzinfo is not None

    stored_chunk = await session.get_one(Chunk, chunk.id)
    assert all(block_id.startswith("blk_") for block_id in stored_chunk.block_ids)
    assert stored_chunk.block_ids == chunk.block_ids
    assert len(stored_chunk.embedding) == EMBEDDING_DIMENSIONS
    assert "lisbon" in stored_chunk.tsv


async def test_vector_keyword_and_trigram_search(session: AsyncSession) -> None:
    _, page, chunk = await _journal_with_a_chunk(session)

    nearest = await session.scalar(
        select(Chunk.id)
        .where(Chunk.page_id == page.id)
        .order_by(Chunk.embedding.cosine_distance(_embedding(7)))
        .limit(1)
    )
    assert nearest == chunk.id

    keyword = await session.scalar(
        select(Chunk.id).where(
            Chunk.page_id == page.id,
            Chunk.tsv.op("@@")(func.websearch_to_tsquery("simple", "lisbon")),
        )
    )
    assert keyword == chunk.id

    fuzzy = await session.scalar(
        select(Block.text).where(
            Block.page_id == page.id, Block.text.op("%")("Flew to Lisbn today")
        )
    )
    assert fuzzy == "Flew to Lisbon today."


async def test_same_file_twice_in_a_journal_is_rejected(session: AsyncSession) -> None:
    journal = Journal(name="Dupes")
    session.add_all([_page(journal, 1, b"same photo"), _page(journal, 2, b"same photo")])
    with pytest.raises(IntegrityError, match="uq_pages_journal_id_sha256"):
        await session.commit()


async def test_pages_can_swap_numbers_in_one_transaction(session: AsyncSession) -> None:
    journal = Journal(name="Swaps")
    first, second = _page(journal, 1), _page(journal, 2)
    session.add_all([journal, first, second])
    await session.commit()

    first.page_number, second.page_number = 2, 1
    await session.commit()

    numbers = await session.execute(
        select(Page.id, Page.page_number).where(Page.journal_id == journal.id)
    )
    assert {page_id: number for page_id, number in numbers} == {first.id: 2, second.id: 1}


async def test_page_numbers_stay_unique(session: AsyncSession) -> None:
    journal = Journal(name="Clash")
    session.add_all([_page(journal, 1, b"a"), _page(journal, 1, b"b")])
    with pytest.raises(IntegrityError, match="uq_pages_journal_id_page_number"):
        await session.commit()


async def test_enum_columns_only_take_api_values(session: AsyncSession) -> None:
    _, page, _ = await _journal_with_a_chunk(session)
    with pytest.raises(IntegrityError, match="ck_pages_status_valid"):
        await session.execute(
            text("UPDATE pages SET status = 'done' WHERE id = :id"),
            {"id": decode(Prefix.PAGE, page.id)},
        )


async def test_ids_with_the_wrong_prefix_are_rejected(session: AsyncSession) -> None:
    with pytest.raises(StatementError, match="Expected a 'pg' TypeID"):
        await session.get(Page, new_id(Prefix.JOURNAL))


async def test_deleting_a_journal_deletes_its_pages_blocks_and_chunks(
    session: AsyncSession,
) -> None:
    journal, page, _ = await _journal_with_a_chunk(session)
    await session.execute(delete(Journal).where(Journal.id == journal.id))
    await session.commit()

    for page_column in (Page.id, Block.page_id, Chunk.page_id):
        assert await session.scalar(select(func.count()).where(page_column == page.id)) == 0


async def test_deleting_a_conversation_deletes_its_messages(session: AsyncSession) -> None:
    conversation = Conversation(title="Lisbon")
    session.add_all(
        [
            conversation,
            Message(conversation=conversation, role=Role.USER, content="When was I in Lisbon?"),
            Message(conversation=conversation, role=Role.ASSISTANT, content="In July [1]."),
        ]
    )
    await session.commit()
    stored = await session.scalars(
        select(Message).where(Message.conversation_id == conversation.id).order_by(Message.id)
    )
    assert [message.role for message in stored] == [Role.USER, Role.ASSISTANT]

    await session.execute(delete(Conversation).where(Conversation.id == conversation.id))
    await session.commit()
    remaining = await session.scalar(
        select(func.count()).where(Message.conversation_id == conversation.id)
    )
    assert remaining == 0
