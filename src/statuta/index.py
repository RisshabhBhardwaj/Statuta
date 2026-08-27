"""Local SQLite FTS index for cited public statutory passages."""

from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from pathlib import Path


def initialize(path: Path) -> None:
    """Create a local FTS5 index with citation-bearing passage records."""
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE VIRTUAL TABLE IF NOT EXISTS passages USING fts5(citation, text)")


def index_passages(path: Path, passages: list[Mapping[str, str]]) -> None:
    """Replace indexed public passages atomically."""
    initialize(path)
    with sqlite3.connect(path) as connection:
        connection.execute("DELETE FROM passages")
        connection.executemany(
            "INSERT INTO passages(citation, text) VALUES (?, ?)",
            [(item["citation"], item["text"]) for item in passages],
        )


def query(path: Path, terms: str) -> tuple[dict[str, str], ...]:
    """Return cited BM25-ranked FTS passages from a caller-managed local index."""
    with sqlite3.connect(path) as connection:
        rows = connection.execute(
            "SELECT citation, text FROM passages WHERE passages MATCH ? ORDER BY bm25(passages)",
            (terms,),
        ).fetchall()
    return tuple({"citation": citation, "text": text} for citation, text in rows)
