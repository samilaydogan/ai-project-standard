"""Deterministic schema-2 manifest; FINAL is a reviewed content label, not publication."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_standard import DISTRIBUTION, INVARIANTS, digest, member, read_json


def payload(root: Path, status: str) -> dict:
    return {
        "schema_version": 2,
        "standard": "ai-project-standard",
        "version": member(root, "VERSION").read_text().strip(),
        "status": status,
        "invariants": sorted(INVARIANTS),
        "files": {name: digest(member(root, name)) for name in sorted(DISTRIBUTION)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--status", choices=("DRAFT", "RC", "FINAL"), default="DRAFT")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = args.root / "standard-release.json"
    if args.check:
        existing = read_json(path)
        if existing != payload(args.root, existing["status"]):
            raise SystemExit("FAIL: ADP-INTEGRITY manifest is stale/incomplete")
        print("PASS: deterministic release manifest")
    else:
        path.write_text(json.dumps(payload(args.root, args.status), indent=2) + "\n")
        print("Generated manifest:", args.status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
