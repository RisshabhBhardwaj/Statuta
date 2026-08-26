"""Synthetic end-to-end tests for five-value verdict assembly."""

from __future__ import annotations

from typing import Any

import pytest

from statuta import VerdictValue, evaluate, evaluate_released, select_rulesets


def _context() -> dict[str, Any]:
    return {
        "query": {
            "occurred_at": "2026-06-01T12:00:00-04:00",
            "requester": {"agency_jurisdiction": "US-AA"},
        },
        "record": {"captured_jurisdiction": "US-AA", "age_days": 22},
    }


def _ruleset(
    *rules: dict[str, Any], effective_at: str = "2026-01-01T00:00:00-05:00"
) -> dict[str, Any]:
    return {
        "ruleset_id": "US-AA",
        "jurisdiction": {"code": "US-AA"},
        "applicability_nexuses": ["capture"],
        "legal_validity": {"effective_at": effective_at, "repealed_or_superseded_at": None},
        "rules": list(rules),
    }


def _rule(rule_id: str, effect: str, condition: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {
        "id": rule_id,
        "effect": effect,
        "applies_when": {"always": True},
        "condition": condition,
        **extra,
    }


@pytest.mark.parametrize(
    ("rules", "expected"),
    [
        ([_rule("AA-PER-001", "permitted", {"always": True})], VerdictValue.PERMITTED),
        ([_rule("AA-PRO-001", "prohibited", {"always": True})], VerdictValue.PROHIBITED),
        (
            [_rule("AA-CON-001", "conditional", {"always": True}, requirements=[{"always": True}])],
            VerdictValue.CONDITIONAL,
        ),
        ([], VerdictValue.UNREGULATED),
        (
            [
                _rule(
                    "AA-PRO-001", "prohibited", {"field": "record.missing", "op": "eq", "value": 1}
                )
            ],
            VerdictValue.INDETERMINATE,
        ),
    ],
)
def test_five_verdict_values(rules: list[dict[str, Any]], expected: VerdictValue) -> None:
    verdict = evaluate(_context(), [_ruleset(*rules)])
    assert verdict.value is expected


def test_prohibition_wins_over_permission_and_time_selection_is_half_open() -> None:
    ruleset = _ruleset(
        _rule("AA-PER-001", "permitted", {"always": True}),
        _rule("AA-PRO-001", "prohibited", {"always": True}),
    )
    assert evaluate(_context(), [ruleset]).deciding_rules == ("AA-PRO-001",)
    expired = _ruleset(
        _rule("AA-PER-001", "permitted", {"always": True}), effective_at="2027-01-01T00:00:00-05:00"
    )
    assert select_rulesets(_context(), [expired]) == ()


def test_obligations_accumulate_without_changing_the_permission_verdict() -> None:
    obligation = _rule(
        "AA-OBL-001", "obligation", {"always": True}, obligations=[{"kind": "audit_log"}]
    )
    permission = _rule("AA-PER-001", "permitted", {"always": True})

    verdict = evaluate(_context(), [_ruleset(obligation, permission)])

    assert verdict.value is VerdictValue.PERMITTED
    assert verdict.obligations == ({"kind": "audit_log"},)


def test_numeric_boundaries_and_missing_nexus_are_safe() -> None:
    retention_limit = _rule(
        "AA-PRO-001", "prohibited", {"field": "record.age_days", "op": "gt", "value": 21}
    )
    at_limit = _context()
    at_limit["record"]["age_days"] = 21
    assert evaluate(at_limit, [_ruleset(retention_limit)]).value is VerdictValue.UNREGULATED
    assert evaluate(_context(), [_ruleset(retention_limit)]).value is VerdictValue.PROHIBITED

    no_nexus = {"query": {"occurred_at": "2026-06-01T12:00:00-04:00"}}
    assert evaluate(no_nexus, [_ruleset(retention_limit)]).value is VerdictValue.UNREGULATED


def test_unknown_applicability_is_indeterminate() -> None:
    requires_capture_jurisdiction = _rule(
        "AA-PRO-001",
        "prohibited",
        {"always": True},
    )
    requires_capture_jurisdiction["applies_when"] = {
        "field": "record.origin_agency_type",
        "op": "eq",
        "value": "law_enforcement",
    }

    verdict = evaluate(_context(), [_ruleset(requires_capture_jurisdiction)])

    assert verdict.value is VerdictValue.INDETERMINATE
    assert verdict.coverage["indeterminate_rules"] == ["AA-PRO-001"]


def test_released_entry_point_rejects_draft_artifacts() -> None:
    with pytest.raises(ValueError, match="only rulesets"):
        evaluate_released(_context(), [_ruleset()])
