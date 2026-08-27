"""Tests for explicit corpus-status and release boundaries."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from statuta.corpus import CorpusError, coverage_summary, released_ruleset_paths, validate_catalog

ROOT = Path(__file__).resolve().parents[1]


def test_public_catalog_is_valid_and_does_not_release_candidates() -> None:
    catalog = json.loads((ROOT / "corpus" / "catalog.json").read_text())
    validate_catalog(catalog)
    assert released_ruleset_paths(catalog) == ()
    assert coverage_summary(catalog) == {"candidate_unreviewed": 3}


def test_absent_rulesets_require_an_explanation() -> None:
    with pytest.raises(CorpusError, match="documented basis"):
        validate_catalog({"jurisdictions": [{"code": "US-AA", "status": "absent_ruleset"}]})
