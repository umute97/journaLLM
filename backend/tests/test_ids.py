import re
import uuid

import pytest

from kritzellm.ids import Prefix, decode, encode, new_id, new_uuid

# From the TypeID spec's valid.yml (https://github.com/jetify-com/typeid/tree/main/spec).
SPEC_VECTORS = [
    ("00000000000000000000000000", "00000000-0000-0000-0000-000000000000"),
    ("00000000000000000000000001", "00000000-0000-0000-0000-000000000001"),
    ("0000000000000000000000000a", "00000000-0000-0000-0000-00000000000a"),
    ("0000000000000000000000000g", "00000000-0000-0000-0000-000000000010"),
    ("00000000000000000000000010", "00000000-0000-0000-0000-000000000020"),
    ("7zzzzzzzzzzzzzzzzzzzzzzzzz", "ffffffff-ffff-ffff-ffff-ffffffffffff"),
    ("0123456789abcdefghjkmnpqrs", "0110c853-1d09-52d8-d73e-1194e95b5f19"),
    ("01h455vb4pex5vsknk084sn02q", "01890a5d-ac96-774b-bcce-b302099a8057"),
]


@pytest.mark.parametrize(("suffix", "value"), SPEC_VECTORS)
def test_spec_vectors(suffix: str, value: str) -> None:
    assert encode(Prefix.PAGE, uuid.UUID(value)) == f"pg_{suffix}"
    assert decode(Prefix.PAGE, f"pg_{suffix}") == uuid.UUID(value)


def test_new_ids_are_uuid7_and_sort_by_creation() -> None:
    first, second = new_uuid(), new_uuid()
    assert first.version == 7
    assert first < second
    assert encode(Prefix.JOURNAL, first) < encode(Prefix.JOURNAL, second)


@pytest.mark.parametrize("prefix", list(Prefix))
def test_ids_match_the_api_pattern(prefix: Prefix) -> None:
    """The same pattern as the TypeID path parameters in `api/schemas/common.py`."""
    typeid = new_id(prefix)
    assert re.fullmatch(rf"{prefix}_[0-7][0-9a-hjkmnp-tv-z]{{25}}", typeid)
    assert encode(prefix, decode(prefix, typeid)) == typeid


@pytest.mark.parametrize(
    "typeid",
    [
        "jrn_01h455vb4pex5vsknk084sn02q",  # another type's prefix
        "01h455vb4pex5vsknk084sn02q",  # no prefix
        "pg_01h455vb4pex5vsknk084sn02",  # too short
        "pg_81h455vb4pex5vsknk084sn02q",  # more than 128 bits
        "pg_01h455vb4pex5vsknk084sn0uq",  # "u" isn't in the alphabet
        "pg_01H455VB4PEX5VSKNK084SN02Q",  # uppercase
    ],
)
def test_decode_rejects_invalid_ids(typeid: str) -> None:
    with pytest.raises(ValueError, match="TypeID"):
        decode(Prefix.PAGE, typeid)
