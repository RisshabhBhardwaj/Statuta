"""Immutable statutory-text snapshot utilities for the compile plane."""

from statuta.acquire.adapters import FileSourceAdapter
from statuta.acquire.snapshots import SnapshotError, build_snapshot, normalize_text, verify_snapshot

__all__ = [
    "FileSourceAdapter",
    "SnapshotError",
    "build_snapshot",
    "normalize_text",
    "verify_snapshot",
]
