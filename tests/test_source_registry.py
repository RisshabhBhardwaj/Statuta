"""Integrity tests for public research-source artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "research" / "sources" / "registry.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_registered_source_files_match_their_recorded_hashes() -> None:
    registry: dict[str, list[dict[str, Any]]] = json.loads(REGISTRY.read_text())
    assert len(registry["sources"]) == 3
    for source in registry["sources"]:
        raw = ROOT / source["raw_path"]
        normalized = ROOT / source["normalized_path"]
        assert raw.is_file()
        assert normalized.is_file()
        assert _sha256(raw) == source["raw_sha256"]
        assert _sha256(normalized) == source["normalized_sha256"]


def test_every_draft_identifies_a_registered_source() -> None:
    registry: dict[str, list[dict[str, Any]]] = json.loads(REGISTRY.read_text())
    source_ids = {source["source_id"] for source in registry["sources"]}
    for draft in (ROOT / "research" / "drafts").glob("US-*.md"):
        text = draft.read_text()
        assert any(source_id in text for source_id in source_ids)
        assert "unreviewed research draft" in text.lower()
        assert "not a released ruleset" in text.lower()
