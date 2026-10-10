"""Write the generated OpenAPI document to api/openapi.json (or check it's up to date)."""

import argparse
import sys
from pathlib import Path

from kritzellm.api.app import render_openapi

SPEC_PATH = Path(__file__).resolve().parents[2] / "api" / "openapi.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the file is out of date")
    args = parser.parse_args()

    rendered = render_openapi()
    if args.check:
        current = SPEC_PATH.read_text() if SPEC_PATH.exists() else ""
        if current != rendered:
            print(f"{SPEC_PATH} is out of date. Run `just api-export`.", file=sys.stderr)
            return 1
        return 0

    SPEC_PATH.write_text(rendered)
    print(f"Wrote {SPEC_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
