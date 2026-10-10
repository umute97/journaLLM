"""TypeIDs: the API's IDs, like `pg_01k7c9a3b5d7e9f1g3h5j7k9m1`.
The database stores the bare UUID.
"""

import uuid
from enum import StrEnum

ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
_VALUES = {char: value for value, char in enumerate(ALPHABET)}
_LENGTH = 26


class Prefix(StrEnum):
    JOURNAL = "jrn"
    PAGE = "pg"
    BLOCK = "blk"
    CONVERSATION = "cnv"
    MESSAGE = "msg"


def new_uuid() -> uuid.UUID:
    return uuid.uuid7()


def new_id(prefix: Prefix) -> str:
    return encode(prefix, new_uuid())


def encode(prefix: Prefix, value: uuid.UUID) -> str:
    number = value.int
    suffix = "".join(ALPHABET[(number >> (5 * shift)) & 31] for shift in reversed(range(_LENGTH)))
    return f"{prefix}_{suffix}"


def decode(prefix: Prefix, typeid: str) -> uuid.UUID:
    """The UUID inside `typeid`. Raises `ValueError` if it isn't a valid `prefix` TypeID."""
    given_prefix, _, suffix = typeid.rpartition("_")
    if given_prefix != prefix:
        raise ValueError(f"Expected a '{prefix}' TypeID, got {typeid!r}")

    if len(suffix) != _LENGTH or suffix[0] > "7" or any(char not in _VALUES for char in suffix):
        raise ValueError(f"Malformed TypeID {typeid!r}")

    number = 0
    for char in suffix:
        number = number << 5 | _VALUES[char]

    return uuid.UUID(int=number)
