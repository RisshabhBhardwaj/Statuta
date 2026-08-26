"""Semantic validation for statuta's closed rule representation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any, Never

COMPARISON_OPERATORS = frozenset({"eq", "ne", "lt", "lte", "gt", "gte", "in", "not_in", "contains"})
NULL_OPERATORS = frozenset({"is_null", "is_not_null"})
ALLOWED_FIELDS = frozenset(
    {
        "query.requester.role",
        "query.requester.employment_status",
        "query.requester.agency_type",
        "query.requester.agency_jurisdiction",
        "query.purpose.code",
        "query.purpose.case_ref",
        "query.authorization.level",
        "query.scope.jurisdictions_searched",
        "query.scope.network_scope",
        "query.scope.time_window_days",
        "query.scope.result_limit",
        "record.captured_jurisdiction",
        "record.age_days",
        "record.kind",
        "record.hotlist_status",
        "record.origin_agency_type",
    }
)


class SemanticValidationError(ValueError):
    """Raised when a schema-shaped artifact violates runtime invariants."""


def _fail(path: str, message: str) -> Never:
    raise SemanticValidationError(f"{path}: {message}")


def _require_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(path, "must be an object")
    return value


def _require_sequence(value: Any, path: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        _fail(path, "must be an array")
    return value


def _validate_predicate(
    predicate: Any, path: str, depth: int = 0, *, recipient_context: bool = False
) -> None:
    if depth > 32:
        _fail(path, "exceeds maximum predicate depth of 32")
    node = _require_mapping(predicate, path)
    keys = set(node)
    if keys == {"always"} and node["always"] is True:
        return
    for combinator in ("all", "any"):
        if keys == {combinator}:
            children = _require_sequence(node[combinator], f"{path}.{combinator}")
            if not children:
                _fail(path, f"{combinator} must not be empty")
            for index, child in enumerate(children):
                _validate_predicate(
                    child,
                    f"{path}.{combinator}[{index}]",
                    depth + 1,
                    recipient_context=recipient_context,
                )
            return
    if keys == {"not"}:
        _validate_predicate(
            node["not"], f"{path}.not", depth + 1, recipient_context=recipient_context
        )
        return
    if node.get("op") == "authorization_at_least":
        if keys != {"field", "op", "value"} or node["field"] != "query.authorization.level":
            _fail(path, "authorization_at_least must name query.authorization.level")
        return
    if node.get("op") == "jurisdiction_matches":
        if keys != {"op", "left", "right"}:
            _fail(path, "jurisdiction_matches requires op, left, and right")
        return
    if node.get("op") == "any_recipient":
        if keys != {"op", "where"}:
            _fail(path, "any_recipient requires op and where")
        _validate_predicate(node["where"], f"{path}.where", depth + 1, recipient_context=True)
        return
    if "field" in node and "op" in node:
        field = node["field"]
        operator = node["op"]
        if field not in ALLOWED_FIELDS and not (
            recipient_context and field in {"agency_type", "agency_jurisdiction", "purpose_code"}
        ):
            _fail(f"{path}.field", f"{field!r} is not in the field registry")
        if operator in COMPARISON_OPERATORS:
            if keys != {"field", "op", "value"}:
                _fail(path, f"{operator} requires exactly field, op, and value")
            return
        if operator in NULL_OPERATORS:
            if keys != {"field", "op"}:
                _fail(path, f"{operator} must not carry a value")
            return
        _fail(f"{path}.op", f"unsupported comparison operator {operator!r}")
    _fail(path, "is not a supported predicate")


def _validate_span(value: Any, path: str) -> None:
    span = _require_sequence(value, path)
    if len(span) != 2 or not all(isinstance(item, int) for item in span):
        _fail(path, "must contain exactly two integer offsets")
    if span[0] < 0 or span[0] >= span[1]:
        _fail(path, "must satisfy 0 <= start < end")


def _validate_rule(rule: Mapping[str, Any], path: str) -> None:
    effect = rule.get("effect")
    _validate_predicate(rule.get("applies_when"), f"{path}.applies_when")
    _validate_predicate(rule.get("condition"), f"{path}.condition")
    requirements = rule.get("requirements", [])
    if effect == "conditional":
        if not requirements:
            _fail(f"{path}.requirements", "conditional rules require at least one requirement")
        for index, requirement in enumerate(
            _require_sequence(requirements, f"{path}.requirements")
        ):
            _validate_predicate(requirement, f"{path}.requirements[{index}]")
    elif requirements:
        _fail(f"{path}.requirements", "only conditional rules may carry requirements in v1")
    obligations = rule.get("obligations", [])
    if effect == "obligation" and not obligations:
        _fail(f"{path}.obligations", "obligation rules require at least one obligation")
    grounding = _require_mapping(rule.get("grounding"), f"{path}.grounding")
    _validate_span(grounding.get("span"), f"{path}.grounding.span")
    interpretations = _require_sequence(rule.get("interpretations", []), f"{path}.interpretations")
    if interpretations:
        defaults = sum(
            item.get("default") is True for item in interpretations if isinstance(item, Mapping)
        )
        if defaults != 1:
            _fail(f"{path}.interpretations", "must contain exactly one default interpretation")
    provenance = _require_mapping(rule.get("provenance"), f"{path}.provenance")
    if provenance.get("method") not in {"hand_encoded", "llm_proposed_human_reviewed"}:
        _fail(f"{path}.provenance.method", "unreviewed rules cannot enter a released ruleset")


def validate_ruleset(ruleset: Mapping[str, Any]) -> None:
    """Validate runtime invariants that JSON Schema alone cannot express."""
    artifact = _require_mapping(ruleset, "ruleset")
    artifact_status = artifact.get("artifact_status")
    if artifact_status not in {"draft", "released"}:
        _fail("ruleset.artifact_status", "must be draft or released")
    validity = _require_mapping(artifact.get("legal_validity"), "ruleset.legal_validity")
    effective = validity.get("effective_at")
    superseded = validity.get("repealed_or_superseded_at")
    temporal_status = validity.get("temporal_status")
    if temporal_status not in {"verified", "unverified"}:
        _fail("ruleset.legal_validity.temporal_status", "must be verified or unverified")
    if artifact_status == "released" and (
        not isinstance(effective, str) or temporal_status != "verified"
    ):
        _fail("ruleset.legal_validity", "released rulesets require a verified effective_at")
    if effective is not None and not isinstance(effective, str):
        _fail("ruleset.legal_validity.effective_at", "must be an ISO-8601 timestamp")
    if superseded is not None and not isinstance(superseded, str):
        _fail(
            "ruleset.legal_validity.repealed_or_superseded_at",
            "must be an ISO-8601 timestamp or null",
        )
    try:
        effective_at = datetime.fromisoformat(effective) if effective is not None else None
        superseded_at = datetime.fromisoformat(superseded) if superseded is not None else None
    except (TypeError, ValueError) as error:
        raise SemanticValidationError(
            "ruleset.legal_validity: invalid ISO-8601 timestamp"
        ) from error
    if effective_at is None and superseded_at is not None:
        _fail("ruleset.legal_validity", "supersession requires an effective_at")
    if effective_at is not None and superseded_at is not None and superseded_at <= effective_at:
        _fail("ruleset.legal_validity", "supersession must be later than effective_at")
    authority = _require_mapping(validity.get("authority"), "ruleset.legal_validity.authority")
    _validate_span(authority.get("span"), "ruleset.legal_validity.authority.span")
    rules = _require_sequence(artifact.get("rules"), "ruleset.rules")
    rule_ids: set[str] = set()
    for index, raw_rule in enumerate(rules):
        rule = _require_mapping(raw_rule, f"ruleset.rules[{index}]")
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or rule_id in rule_ids:
            _fail(f"ruleset.rules[{index}].id", "must be a unique string")
        rule_ids.add(rule_id)
        _validate_rule(rule, f"ruleset.rules[{index}]")
        if artifact_status == "released" and rule["provenance"].get("reviewed_by") is None:
            _fail(f"ruleset.rules[{index}].provenance", "released rules require independent review")
    for index, raw_rule in enumerate(rules):
        for exception in _require_sequence(
            raw_rule.get("exceptions", []), f"ruleset.rules[{index}].exceptions"
        ):
            if exception not in rule_ids:
                _fail(f"ruleset.rules[{index}].exceptions", f"unknown rule reference {exception!r}")
