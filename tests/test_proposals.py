"""Tests for dual-proposal agreement and reviewer triage."""

from statuta.compile.proposals import ProposalPair, review_priority


def test_dual_model_agreement_uses_structure_not_description() -> None:
    first = {"rule_type": "retention", "effect": "prohibited", "condition": {"always": True}}
    second = {**first, "description": "different prose"}
    pair = ProposalPair("p1", "model-a", "model-b", (first,), (second,))
    assert pair.agreement
    assert review_priority(pair) == (2, "prohibition candidate")


def test_disagreement_is_first_in_review_queue() -> None:
    pair = ProposalPair("p1", "model-a", "model-b", (), ({"effect": "permitted"},))
    assert not pair.agreement
    assert review_priority(pair) == (0, "model disagreement")
