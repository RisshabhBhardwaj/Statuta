"""Tests for ruleset semantic validation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from statuta import SemanticValidationError, validate_ruleset


def _ruleset() -> dict[str, Any]:
    return {
        "artifact_status": "draft",
        "legal_validity": {
            "effective_at": "2026-01-01T00:00:00-05:00",
            "repealed_or_superseded_at": None,
            "temporal_status": "verified",
            "authority": {"span": [1, 2]},
        },
        "rules": [
            {
                "id": "CT-RET-001",
                "effect": "conditional",
                "applies_when": {"always": True},
                "condition": {"field": "record.age_days", "op": "gt", "value": 14},
                "requirements": [
                    {
                        "field": "query.purpose.case_ref",
                        "op": "is_not_null",
                    }
                ],
                "grounding": {"span": [3, 4]},
                "interpretations": [{"id": "narrow", "default": True}],
                "provenance": {"method": "hand_encoded"},
                "exceptions": [],
            }
        ],
    }


def test_accepts_a_valid_released_ruleset() -> None:
    validate_ruleset(_ruleset())


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda value: value["rules"][0].pop("requirements"), "conditional rules require"),
        (
            lambda value: value["rules"][0].update(
                {"condition": {"field": "record.age_days", "op": "gt"}}
            ),
            "requires exactly field, op, and value",
        ),
        (
            lambda value: value["rules"][0].update(
                {"condition": {"field": "record.age_days", "op": "is_null", "value": None}}
            ),
            "must not carry a value",
        ),
        (
            lambda value: value["rules"][0].update(
                {"condition": {"field": "not.a.real.field", "op": "eq", "value": "x"}}
            ),
            "field registry",
        ),
        (lambda value: value["rules"][0]["grounding"].update({"span": [4, 4]}), "start < end"),
        (
            lambda value: value["rules"][0].update(
                {"interpretations": [{"id": "one", "default": False}]}
            ),
            "exactly one default",
        ),
        (
            lambda value: value["rules"][0]["provenance"].update(
                {"method": "llm_proposed_unreviewed"}
            ),
            "unreviewed rules",
        ),
        (
            lambda value: value["rules"][0].update({"exceptions": ["MISSING"]}),
            "unknown rule reference",
        ),
        (
            lambda value: value["legal_validity"].update(
                {"repealed_or_superseded_at": "2025-12-31T23:59:59-05:00"}
            ),
            "supersession must be later",
        ),
        (
            lambda value: value["legal_validity"].update({"effective_at": "not-a-timestamp"}),
            "invalid ISO-8601",
        ),
        (
            lambda value: value.update({"artifact_status": "released"}),
            "released rules require independent review",
        ),
        (
            lambda value: (
                value["legal_validity"].update(
                    {"effective_at": None, "temporal_status": "unverified"}
                )
                or value.update({"artifact_status": "released"})
            ),
            "released rulesets require a verified effective_at",
        ),
        (
            lambda value: value["rules"][0].update({"requirements": "not-an-array"}),
            "must be an array",
        ),
        (
            lambda value: value["rules"][0].update(
                {"effect": "obligation", "obligations": [], "requirements": []}
            ),
            "obligation rules require",
        ),
        (
            lambda value: value["rules"][0].update({"effect": "permitted"}),
            "only conditional rules",
        ),
        (
            lambda value: value["rules"][0].update(
                {"condition": {"field": "record.age_days", "op": "not_an_operator", "value": 1}}
            ),
            "unsupported comparison operator",
        ),
    ],
)
def test_rejects_semantically_invalid_rulesets(mutation: Any, message: str) -> None:
    artifact = deepcopy(_ruleset())
    mutation(artifact)
    with pytest.raises(SemanticValidationError, match=message):
        validate_ruleset(artifact)


@pytest.mark.parametrize(
    "predicate",
    [
        {"all": [{"always": True}, {"not": {"always": True}}]},
        {"op": "authorization_at_least", "field": "query.authorization.level", "value": "warrant"},
        {
            "op": "jurisdiction_matches",
            "left": "query.requester.agency_jurisdiction",
            "right": "record.captured_jurisdiction",
        },
        {"op": "any_recipient", "where": {"field": "agency_type", "op": "eq", "value": "federal"}},
    ],
)
def test_accepts_each_supported_predicate_shape(predicate: dict[str, Any]) -> None:
    artifact = _ruleset()
    artifact["rules"][0]["condition"] = predicate
    validate_ruleset(artifact)
