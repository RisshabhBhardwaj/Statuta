"""Explicit, offline-friendly source adapters for public statutory text."""

from __future__ import annotations

from pathlib import Path


class FileSourceAdapter:
    """Read a caller-selected public source file without hidden network access."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def fetch_text(self) -> str:
        """Return source text exactly as recorded by the caller."""
        return self.path.read_text()
