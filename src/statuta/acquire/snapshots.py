"""Deterministic normalization and content-addressing for statutory sources."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Mapping
from typing import Any


class SnapshotError(ValueError):
    """Raised when a snapshot's recorded immutable content does not verify."""


NORMALIZATION_VERSION = "1.0.0"


def normalize_text(raw_text: str) -> str:
    """Normalize source text exactly once before deriving stable offsets and hashes."""
    normalized = unicodedata.normalize("NFC", raw_text)
    normalized = normalized.translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"}))
    normalized = normalized.replace("\u00ad", "").replace("\ufb01", "fi").replace("\ufb02", "fl")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip() + "\n"


def _sha256(value: str | bytes) -> str:
    payload = value if isinstance(value, bytes) else value.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_snapshot(
    *,
    source_id: str,
    jurisdiction: str,
    citation: str,
    retrieved_at: str,
    raw_text: str,
    source_url: str,
) -> dict[str, Any]:
    """Create an immutable, self-describing snapshot record without I/O."""
    normalized = normalize_text(raw_text)
    return {
        "source_id": source_id,
        "jurisdiction": jurisdiction,
        "citation": citation,
        "source_url": source_url,
        "retrieved_at": retrieved_at,
        "raw_sha256": _sha256(raw_text),
        "normalized_sha256": _sha256(normalized),
        "normalization_version": NORMALIZATION_VERSION,
        "normalized_text": normalized,
    }


def verify_snapshot(snapshot: Mapping[str, Any], raw_text: str) -> None:
    """Verify raw and normalized hashes; no post-hash transformation is allowed."""
    if snapshot.get("normalization_version") != NORMALIZATION_VERSION:
        raise SnapshotError("unsupported normalization version")
    if snapshot.get("raw_sha256") != _sha256(raw_text):
        raise SnapshotError("raw source hash does not match")
    normalized = normalize_text(raw_text)
    if snapshot.get("normalized_text") != normalized:
        raise SnapshotError("normalized text does not match recorded snapshot")
    if snapshot.get("normalized_sha256") != _sha256(normalized):
        raise SnapshotError("normalized source hash does not match")
