"""Tests for immutable source snapshot construction."""

from __future__ import annotations

import pytest

from statuta.acquire import SnapshotError, build_snapshot, normalize_text, verify_snapshot


def test_normalization_is_deterministic_and_precedes_hashing() -> None:
    raw = "  A\r\n\r\n\r\n‘data’  \ufb01le\u00ad  "
    assert normalize_text(raw) == "A\n\n'data' file\n"
    snapshot = build_snapshot(
        source_id="US-AA-1",
        jurisdiction="US-AA",
        citation="Synthetic § 1",
        retrieved_at="2026-08-26T00:00:00Z",
        raw_text=raw,
        source_url="https://example.test/statute",
    )
    verify_snapshot(snapshot, raw)


def test_snapshot_rejects_post_hash_text_changes() -> None:
    snapshot = build_snapshot(
        source_id="US-AA-1",
        jurisdiction="US-AA",
        citation="Synthetic § 1",
        retrieved_at="2026-08-26T00:00:00Z",
        raw_text="Original text",
        source_url="https://example.test/statute",
    )
    with pytest.raises(SnapshotError, match="raw source hash"):
        verify_snapshot(snapshot, "Changed text")
