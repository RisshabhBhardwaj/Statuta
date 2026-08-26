"""Gold-scenario schema and runtime conformance tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from jsonschema import Draft202012Validator

from statuta import ScenarioError, VerdictValue, evaluate, run_scenario

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "gold-scenario.schema.json").read_text())


def _ruleset() -> dict[str, Any]:
    return {
        "ruleset_id": "US-AA",
        "ruleset_version": "0.0.0-synthetic",
        "jurisdiction": {"code": "US-AA"},
        "applicability_nexuses": ["capture"],
        "legal_validity": {
            "effective_at": "2026-01-01T00:00:00-05:00",
            "repealed_or_superseded_at": None,
        },
        "rules": [
            {
                "id": "AA-RET-001",
                "effect": "prohibited",
                "applies_when": {"always": True},
                "condition": {"field": "record.age_days", "op": "gt", "value": 21},
            }
        ],
    }


def test_synthetic_gold_scenarios_are_schema_valid_and_conform() -> None:
    validator = Draft202012Validator(SCHEMA)
    for path in sorted((ROOT / "gold" / "synthetic").glob("*.json")):
        scenario: dict[str, Any] = json.loads(path.read_text())
        validator.validate(scenario)
        assert run_scenario(scenario, [_ruleset()]).passed


def test_scenario_runner_rejects_malformed_deciding_rule_expectation() -> None:
    with pytest.raises(ScenarioError, match="array of strings"):
        run_scenario(
            {
                "id": "broken",
                "context": {},
                "expected_verdict": "unregulated",
                "expected_deciding_rules": "x",
            },
            [],
        )


@given(include_prohibition=st.booleans(), include_permission=st.booleans())
def test_prohibition_always_dominates_permission(
    include_prohibition: bool, include_permission: bool
) -> None:
    rules: list[dict[str, Any]] = []
    if include_permission:
        rules.append(
            {
                "id": "AA-PER-001",
                "effect": "permitted",
                "applies_when": {"always": True},
                "condition": {"always": True},
            }
        )
    if include_prohibition:
        rules.append(
            {
                "id": "AA-PRO-001",
                "effect": "prohibited",
                "applies_when": {"always": True},
                "condition": {"always": True},
            }
        )
    ruleset = _ruleset()
    ruleset["rules"] = rules
    context = json.loads((ROOT / "gold" / "synthetic" / "prohibited-retention.json").read_text())[
        "context"
    ]

    verdict = evaluate(context, [ruleset])

    if include_prohibition:
        assert verdict.value is VerdictValue.PROHIBITED
    elif include_permission:
        assert verdict.value is VerdictValue.PERMITTED
    else:
        assert verdict.value is VerdictValue.UNREGULATED
