"""Mechanical grounding verification against registered normalized snapshots."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any


class GroundingError(ValueError):
    """Raised when a draft rule does not match its declared source span."""


def verify_grounding(rule: Mapping[str, Any], snapshot_text: str) -> None:
    """Verify one literal quote and its half-open character span."""
    grounding = rule["grounding"]
    quote = grounding["quote"]
    start, end = grounding["span"]
    if snapshot_text[start:end] != quote:
        raise GroundingError(f"{rule['id']}: quote does not match declared snapshot span")


def read_snapshot(path: Path) -> str:
    """Read an immutable normalized-text snapshot for grounding checks."""
    return path.read_text()
