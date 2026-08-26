"""Deterministic evaluation over synthetic or released ruleset artifacts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from statuta.core.predicate import TruthValue, evaluate_predicate
from statuta.core.validation import validate_ruleset


class VerdictValue(StrEnum):
    """The public five-value evaluator result."""

    PERMITTED = "permitted"
    PROHIBITED = "prohibited"
    CONDITIONAL = "conditional"
    UNREGULATED = "unregulated"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class Verdict:
    """A deterministic decision plus the evidence and coverage behind it."""

    value: VerdictValue
    deciding_rules: tuple[str, ...]
    requirements_satisfied: bool | None
    obligations: tuple[Mapping[str, Any], ...]
    resolution_path: tuple[str, ...]
    coverage: Mapping[str, Any]


def _at(value: Mapping[str, Any], *path: str) -> Any:
    current: Any = value
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def _nexuses(context: Mapping[str, Any]) -> dict[str, set[str]]:
    searched = _at(context, "query", "scope", "jurisdictions_searched")
    return {
        "actor": {
            value for value in [_at(context, "query", "requester", "agency_jurisdiction")] if value
        },
        "capture": {value for value in [_at(context, "record", "captured_jurisdiction")] if value},
        "search": set(searched)
        if isinstance(searched, Sequence) and not isinstance(searched, str)
        else set(),
    }


def _is_current(ruleset: Mapping[str, Any], occurred_at: datetime) -> bool:
    validity = ruleset["legal_validity"]
    effective = validity.get("effective_at")
    if not isinstance(effective, str):
        return False
    start = datetime.fromisoformat(effective)
    end_value = validity.get("repealed_or_superseded_at")
    end = datetime.fromisoformat(end_value) if isinstance(end_value, str) else None
    return occurred_at >= start and (end is None or occurred_at < end)


def select_rulesets(
    context: Mapping[str, Any], rulesets: Sequence[Mapping[str, Any]]
) -> tuple[Mapping[str, Any], ...]:
    """Select time-valid rulesets whose declared nexus appears in the context."""
    occurred_value = _at(context, "query", "occurred_at")
    if not isinstance(occurred_value, str):
        return ()
    occurred_at = datetime.fromisoformat(occurred_value)
    nexuses = _nexuses(context)
    selected: list[Mapping[str, Any]] = []
    for ruleset in rulesets:
        code = _at(ruleset, "jurisdiction", "code")
        declared = ruleset.get("applicability_nexuses", [])
        if not isinstance(code, str) or not _is_current(ruleset, occurred_at):
            continue
        if any(code in nexuses.get(nexus, set()) for nexus in declared):
            selected.append(ruleset)
    return tuple(selected)


def evaluate(context: Mapping[str, Any], rulesets: Sequence[Mapping[str, Any]]) -> Verdict:
    """Evaluate supplied rulesets without I/O or model participation."""
    selected = select_rulesets(context, rulesets)
    fired: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []
    indeterminate: list[str] = []
    path = [f"selected {ruleset['ruleset_id']}" for ruleset in selected]
    for ruleset in selected:
        for rule in ruleset.get("rules", []):
            applies = evaluate_predicate(rule["applies_when"], context)
            if applies is TruthValue.UNKNOWN:
                indeterminate.append(rule["id"])
                continue
            if applies is not TruthValue.TRUE:
                continue
            result = evaluate_predicate(rule["condition"], context)
            if result is TruthValue.UNKNOWN:
                indeterminate.append(rule["id"])
                continue
            if result is TruthValue.TRUE:
                fired.append((ruleset, rule))
    coverage: dict[str, Any] = {
        "jurisdictions_evaluated": [ruleset["jurisdiction"]["code"] for ruleset in selected],
        "indeterminate_rules": indeterminate,
    }
    obligations = tuple(
        obligation
        for _, rule in fired
        if rule["effect"] == "obligation"
        for obligation in rule.get("obligations", [])
    )
    prohibited = [(rs, rule) for rs, rule in fired if rule["effect"] == "prohibited"]
    if prohibited:
        rules = tuple(sorted(rule["id"] for _, rule in prohibited))
        return Verdict(
            VerdictValue.PROHIBITED,
            rules,
            None,
            obligations,
            tuple(path + ["prohibition fired"]),
            coverage,
        )
    conditional = [(rs, rule) for rs, rule in fired if rule["effect"] == "conditional"]
    for _, rule in conditional:
        requirement_values = [
            evaluate_predicate(item, context) for item in rule.get("requirements", [])
        ]
        if TruthValue.UNKNOWN in requirement_values:
            indeterminate.append(rule["id"])
        elif all(value is TruthValue.TRUE for value in requirement_values):
            return Verdict(
                VerdictValue.CONDITIONAL,
                (rule["id"],),
                True,
                obligations,
                tuple(path + ["conditional rule satisfied"]),
                coverage,
            )
    permitted = [(rs, rule) for rs, rule in fired if rule["effect"] == "permitted"]
    if permitted:
        rules = tuple(sorted(rule["id"] for _, rule in permitted))
        return Verdict(
            VerdictValue.PERMITTED,
            rules,
            None,
            obligations,
            tuple(path + ["permission fired"]),
            coverage,
        )
    if indeterminate:
        return Verdict(
            VerdictValue.INDETERMINATE,
            (),
            None,
            obligations,
            tuple(path + ["required facts missing"]),
            coverage,
        )
    return Verdict(
        VerdictValue.UNREGULATED,
        (),
        None,
        obligations,
        tuple(path + ["no rule fired"]),
        coverage,
    )


def evaluate_released(context: Mapping[str, Any], rulesets: Sequence[Mapping[str, Any]]) -> Verdict:
    """Evaluate only semantically validated, released rulesets.

    ``evaluate`` intentionally accepts minimal synthetic fixtures for runtime
    tests. Production callers must use this entry point so a draft corpus
    cannot be evaluated by accident.
    """
    for ruleset in rulesets:
        if ruleset.get("artifact_status") != "released":
            msg = "evaluate_released accepts only rulesets with artifact_status='released'"
            raise ValueError(msg)
        validate_ruleset(ruleset)
    return evaluate(context, rulesets)
