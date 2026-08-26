"""Tests for compile-plane mechanical proposal gates."""

from statuta.compile import gate_candidate, structurally_equivalent


def _candidate(quote: str, span: list[int]) -> dict[str, object]:
    return {
        "rule_type": "retention",
        "effect": "prohibited",
        "applies_when": {"always": True},
        "condition": {"field": "record.age_days", "op": "gt", "value": 21},
        "grounding": {"quote": quote, "span": span},
    }


def test_grounding_gate_discards_fabricated_quote() -> None:
    result = gate_candidate(
        _candidate("fabricated", [0, 9]), "Data shall be deleted after 21 days."
    )
    assert not result.accepted
    assert "G2_grounding" in result.discarded_by


def test_structural_equivalence_ignores_prose_but_not_thresholds() -> None:
    first = _candidate("Data", [0, 4])
    second = _candidate("Data", [0, 4])
    second["description"] = "different prose"
    assert structurally_equivalent(first, second)
    second["condition"] = {"field": "record.age_days", "op": "gt", "value": 22}
    assert not structurally_equivalent(first, second)
