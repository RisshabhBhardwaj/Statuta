"""Append-only JSONL storage for transparency-log leaves."""

from __future__ import annotations

import json
from pathlib import Path


def append_leaf(path: Path, leaf: bytes) -> int:
    """Append an opaque leaf atomically as one JSONL record and return its index."""
    path.parent.mkdir(parents=True, exist_ok=True)
    index = len(read_leaves(path))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"leaf_hex": leaf.hex()}, separators=(",", ":")) + "\n")
        handle.flush()
    return index


def read_leaves(path: Path) -> tuple[bytes, ...]:
    """Read only well-formed append-only leaf records."""
    if not path.exists():
        return ()
    return tuple(
        bytes.fromhex(json.loads(line)["leaf_hex"]) for line in path.read_text().splitlines()
    )
