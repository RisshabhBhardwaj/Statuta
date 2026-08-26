"""Pure three-valued evaluation for the closed predicate grammar."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Any


class TruthValue(StrEnum):
    """Kleene truth values used for every predicate result."""

    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


_MISSING = object()
_AUTHORIZATION_RANK = {
    "none": 0,
    "supervisor": 1,
    "agency_head": 2,
    "court_order": 3,
    "warrant": 4,
}


def _field_value(context: Mapping[str, Any], path: str) -> Any:
    value: Any = context
    for segment in path.split("."):
        if not isinstance(value, Mapping) or segment not in value:
            return _MISSING
        value = value[segment]
    return value


def _all(values: Sequence[TruthValue]) -> TruthValue:
    if TruthValue.FALSE in values:
        return TruthValue.FALSE
    if TruthValue.UNKNOWN in values:
        return TruthValue.UNKNOWN
    return TruthValue.TRUE


def _any(values: Sequence[TruthValue]) -> TruthValue:
    if TruthValue.TRUE in values:
        return TruthValue.TRUE
    if TruthValue.UNKNOWN in values:
        return TruthValue.UNKNOWN
    return TruthValue.FALSE


def _compare(actual: Any, operator: str, expected: Any) -> TruthValue:
    if actual is _MISSING:
        return TruthValue.UNKNOWN
    try:
        if operator == "eq":
            result = actual == expected
        elif operator == "ne":
            result = actual != expected
        elif operator == "lt":
            result = actual < expected
        elif operator == "lte":
            result = actual <= expected
        elif operator == "gt":
            result = actual > expected
        elif operator == "gte":
            result = actual >= expected
        elif operator == "in":
            result = actual in expected
        elif operator == "not_in":
            result = actual not in expected
        elif operator == "contains":
            result = expected in actual
        elif operator == "is_null":
            result = actual is None
        elif operator == "is_not_null":
            result = actual is not None
        else:
            return TruthValue.UNKNOWN
    except TypeError:
        return TruthValue.UNKNOWN
    return TruthValue.TRUE if result else TruthValue.FALSE


def _authorization_at_least(context: Mapping[str, Any], expected: Any) -> TruthValue:
    actual = _field_value(context, "query.authorization.level")
    if actual is _MISSING or actual == "unknown" or expected == "unknown":
        return TruthValue.UNKNOWN
    if actual == "exigent" or expected == "exigent":
        return TruthValue.TRUE if actual == expected else TruthValue.UNKNOWN
    if actual not in _AUTHORIZATION_RANK or expected not in _AUTHORIZATION_RANK:
        return TruthValue.UNKNOWN
    return (
        TruthValue.TRUE
        if _AUTHORIZATION_RANK[actual] >= _AUTHORIZATION_RANK[expected]
        else TruthValue.FALSE
    )


def evaluate_predicate(predicate: Mapping[str, Any], context: Mapping[str, Any]) -> TruthValue:
    """Evaluate one closed predicate without I/O, time, or external state."""
    if predicate.get("always") is True:
        return TruthValue.TRUE
    if "all" in predicate:
        values = [evaluate_predicate(child, context) for child in predicate["all"]]
        return _all(values)
    if "any" in predicate:
        values = [evaluate_predicate(child, context) for child in predicate["any"]]
        return _any(values)
    if "not" in predicate:
        value = evaluate_predicate(predicate["not"], context)
        if value is TruthValue.UNKNOWN:
            return value
        return TruthValue.FALSE if value is TruthValue.TRUE else TruthValue.TRUE
    operator = predicate.get("op")
    if operator == "authorization_at_least":
        return _authorization_at_least(context, predicate.get("value"))
    if operator == "jurisdiction_matches":
        left = _field_value(context, predicate.get("left", ""))
        right = _field_value(context, predicate.get("right", ""))
        return _compare(left, "eq", right) if right is not _MISSING else TruthValue.UNKNOWN
    if operator == "any_recipient":
        recipients = _field_value(context, "disclosure.recipients")
        if (
            recipients is _MISSING
            or not isinstance(recipients, Sequence)
            or isinstance(recipients, str)
        ):
            return TruthValue.UNKNOWN
        return _any(
            [
                evaluate_predicate(predicate["where"], recipient)
                for recipient in recipients
                if isinstance(recipient, Mapping)
            ]
        )
    field = predicate.get("field")
    if not isinstance(field, str) or not isinstance(operator, str):
        return TruthValue.UNKNOWN
    return _compare(_field_value(context, field), operator, predicate.get("value"))
