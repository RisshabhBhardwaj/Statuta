"""Tests for deterministic three-valued predicate evaluation."""

from __future__ import annotations

from typing import Any

import pytest

from statuta import TruthValue, evaluate_predicate

CONTEXT: dict[str, Any] = {
    "query": {
        "purpose": {"code": "criminal_investigation", "case_ref": None},
        "authorization": {"level": "warrant"},
        "requester": {"agency_jurisdiction": "US-CT"},
    },
    "record": {"age_days": 21, "captured_jurisdiction": "US-CT"},
    "disclosure": {"recipients": [{"agency_type": "federal"}, {"agency_type": "local"}]},
}


@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        ({"always": True}, TruthValue.TRUE),
        ({"field": "record.age_days", "op": "gt", "value": 20}, TruthValue.TRUE),
        ({"field": "record.age_days", "op": "gte", "value": 21}, TruthValue.TRUE),
        ({"field": "record.age_days", "op": "lt", "value": 21}, TruthValue.FALSE),
        ({"field": "record.age_days", "op": "lte", "value": 20}, TruthValue.FALSE),
        (
            {"field": "query.purpose.code", "op": "eq", "value": "criminal_investigation"},
            TruthValue.TRUE,
        ),
        (
            {"field": "query.purpose.code", "op": "ne", "value": "traffic_enforcement"},
            TruthValue.TRUE,
        ),
        (
            {"field": "query.purpose.code", "op": "in", "value": ["criminal_investigation"]},
            TruthValue.TRUE,
        ),
        (
            {"field": "query.purpose.code", "op": "not_in", "value": ["traffic_enforcement"]},
            TruthValue.TRUE,
        ),
        (
            {"field": "query.purpose.code", "op": "contains", "value": "investigation"},
            TruthValue.TRUE,
        ),
        ({"field": "query.purpose.case_ref", "op": "is_null"}, TruthValue.TRUE),
        ({"field": "query.purpose.case_ref", "op": "is_not_null"}, TruthValue.FALSE),
        ({"field": "record.missing", "op": "eq", "value": 1}, TruthValue.UNKNOWN),
    ],
)
def test_comparisons(predicate: dict[str, Any], expected: TruthValue) -> None:
    assert evaluate_predicate(predicate, CONTEXT) is expected


@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        (
            {"all": [{"always": True}, {"field": "record.missing", "op": "eq", "value": 1}]},
            TruthValue.UNKNOWN,
        ),
        (
            {
                "all": [
                    {"field": "record.age_days", "op": "lt", "value": 0},
                    {"field": "record.missing", "op": "eq", "value": 1},
                ]
            },
            TruthValue.FALSE,
        ),
        (
            {
                "any": [
                    {"field": "record.age_days", "op": "lt", "value": 0},
                    {"field": "record.missing", "op": "eq", "value": 1},
                ]
            },
            TruthValue.UNKNOWN,
        ),
        (
            {"any": [{"always": True}, {"field": "record.missing", "op": "eq", "value": 1}]},
            TruthValue.TRUE,
        ),
        ({"not": {"always": True}}, TruthValue.FALSE),
        ({"not": {"field": "record.missing", "op": "eq", "value": 1}}, TruthValue.UNKNOWN),
    ],
)
def test_kleene_combinators(predicate: dict[str, Any], expected: TruthValue) -> None:
    assert evaluate_predicate(predicate, CONTEXT) is expected


@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        ({"op": "authorization_at_least", "value": "supervisor"}, TruthValue.TRUE),
        ({"op": "authorization_at_least", "value": "warrant"}, TruthValue.TRUE),
        ({"op": "authorization_at_least", "value": "exigent"}, TruthValue.UNKNOWN),
        (
            {
                "op": "jurisdiction_matches",
                "left": "query.requester.agency_jurisdiction",
                "right": "record.captured_jurisdiction",
            },
            TruthValue.TRUE,
        ),
        (
            {
                "op": "any_recipient",
                "where": {"field": "agency_type", "op": "eq", "value": "federal"},
            },
            TruthValue.TRUE,
        ),
    ],
)
def test_domain_operators(predicate: dict[str, Any], expected: TruthValue) -> None:
    assert evaluate_predicate(predicate, CONTEXT) is expected


def test_unknown_authorization_and_empty_recipients_are_not_permission() -> None:
    context = {"query": {"authorization": {"level": "unknown"}}, "disclosure": {"recipients": []}}
    assert (
        evaluate_predicate({"op": "authorization_at_least", "value": "warrant"}, context)
        is TruthValue.UNKNOWN
    )
    assert (
        evaluate_predicate({"op": "any_recipient", "where": {"always": True}}, context)
        is TruthValue.FALSE
    )
