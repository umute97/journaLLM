"""Column types."""

import uuid
from typing import Any

from sqlalchemy import Dialect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator

from kritzellm.ids import Prefix, decode, encode


class TypeId(TypeDecorator[str]):
    """A `uuid` column that Python sees as a TypeID string, e.g. `pg_01k7c9…`."""

    impl = UUID
    cache_ok = True

    def __init__(self, prefix: Prefix) -> None:
        super().__init__(as_uuid=True)
        self.prefix = prefix

    def process_bind_param(self, value: str | None, dialect: Dialect) -> uuid.UUID | None:
        return None if value is None else decode(self.prefix, value)

    def process_result_value(self, value: Any, dialect: Dialect) -> str | None:
        return None if value is None else encode(self.prefix, value)
