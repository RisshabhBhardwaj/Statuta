"""Validation and grounding tests for explicitly unreleased candidate rulesets."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from statuta import GroundingError, read_snapshot, validate_ruleset, verify_grounding

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema"
RULE_SCHEMA = json.loads((SCHEMA_DIR / "rule.schema.json").read_text())
RULESET_SCHEMA = json.loads((SCHEMA_DIR / "ruleset.schema.json").read_text())
SCHEMA_REGISTRY = Registry().with_resource(RULE_SCHEMA["$id"], Resource.from_contents(RULE_SCHEMA))


def _candidates() -> list[Path]:
    return sorted((ROOT / "research" / "candidates").glob("US-*/*.json"))


def test_candidate_rulesets_are_schema_valid_semantic_drafts_and_span_grounded() -> None:
    validator = Draft202012Validator(RULESET_SCHEMA, registry=SCHEMA_REGISTRY)
    for path in _candidates():
        ruleset: dict[str, Any] = json.loads(path.read_text())
        validator.validate(ruleset)
        validate_ruleset(ruleset)
        assert ruleset["artifact_status"] == "draft"
        snapshot_hash = ruleset["legal_validity"]["authority"]["snapshot_sha256"]
        source = next(
            source
            for source in json.loads((ROOT / "research" / "sources" / "registry.json").read_text())[
                "sources"
            ]
            if source["normalized_sha256"] == snapshot_hash
        )
        snapshot = read_snapshot(ROOT / source["normalized_path"])
        for rule in ruleset["rules"]:
            verify_grounding(rule, snapshot)


def test_grounding_rejects_a_quote_that_does_not_match_its_span() -> None:
    ruleset: dict[str, Any] = json.loads(_candidates()[0].read_text())
    rule = deepcopy(ruleset["rules"][0])
    rule["grounding"]["quote"] = "fabricated statutory text"
    with pytest.raises(GroundingError, match="does not match"):
        verify_grounding(rule, "x" * 70000)
