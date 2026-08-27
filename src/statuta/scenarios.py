"""Seeded, content-free fixtures and conformance checks for evaluator testing."""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from statuta.core.evaluate import Verdict, evaluate


class ScenarioError(ValueError):
    """Raised when a gold scenario is not usable as a conformance contract."""


@dataclass(frozen=True)
class ScenarioResult:
    """The reproducible result of running one gold scenario."""

    scenario_id: str
    expected_verdict: str
    actual_verdict: str
    expected_deciding_rules: tuple[str, ...] | None
    actual_deciding_rules: tuple[str, ...]
    verdict: Verdict

    @property
    def passed(self) -> bool:
        """Whether the scenario's declared expectation agrees with the evaluator."""
        return self.expected_verdict == self.actual_verdict and (
            self.expected_deciding_rules is None
            or self.expected_deciding_rules == self.actual_deciding_rules
        )


def generate_contexts(seed: int, count: int) -> list[dict[str, Any]]:
    """Generate reproducible synthetic contexts without surveillance content."""
    randomizer = random.Random(seed)
    return [
        {
            "query": {
                "occurred_at": "2026-06-01T12:00:00-04:00",
                "requester": {"agency_jurisdiction": "US-AA"},
            },
            "record": {"captured_jurisdiction": "US-AA", "age_days": randomizer.randrange(0, 61)},
        }
        for _ in range(count)
    ]


def numeric_boundary_contexts(rulesets: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Generate synthetic n-1/n/n+1 contexts for every numeric rule threshold."""
    contexts: list[dict[str, Any]] = []
    for ruleset in rulesets:
        for rule in ruleset.get("rules", []):
            condition = rule.get("condition", {})
            if not isinstance(condition, Mapping) or not isinstance(condition.get("value"), int):
                continue
            field = condition.get("field")
            if field != "record.age_days":
                continue
            for value in (condition["value"] - 1, condition["value"], condition["value"] + 1):
                contexts.append(
                    {
                        "query": {"occurred_at": "2026-06-01T12:00:00-04:00"},
                        "record": {
                            "captured_jurisdiction": ruleset["jurisdiction"]["code"],
                            "age_days": value,
                        },
                    }
                )
    return contexts


def generate_gold_suite(seed: int, count: int = 150) -> list[dict[str, Any]]:
    """Create a reproducible, content-free five-class synthetic scenario suite."""
    classes = ("clear", "boundary", "missing_field", "cross_jurisdiction", "unregulated")
    contexts = generate_contexts(seed, count)
    suite: list[dict[str, Any]] = []
    for index, raw_context in enumerate(contexts):
        context: dict[str, Any] = raw_context
        scenario_class = classes[index % len(classes)]
        item: dict[str, Any] = {
            "id": f"synthetic-{index:03d}",
            "scenario_class": scenario_class,
            "context": context,
        }
        if scenario_class == "missing_field":
            item["context"] = {
                "query": context["query"],
                "record": {"captured_jurisdiction": "US-AA"},
            }
        if scenario_class == "cross_jurisdiction":
            query: dict[str, Any] = item["context"]["query"]
            query["scope"] = {"jurisdictions_searched": ["US-AA", "US-BB"]}
        if scenario_class == "unregulated":
            record: dict[str, Any] = item["context"]["record"]
            record["captured_jurisdiction"] = "US-ZZ"
        suite.append(item)
    return suite


def run_scenario(
    scenario: Mapping[str, Any], rulesets: Sequence[Mapping[str, Any]]
) -> ScenarioResult:
    """Evaluate a schema-shaped synthetic or reviewed-statute scenario.

    The caller chooses the evaluator input deliberately; this function never
    discovers corpus files, reaches the network, or promotes a draft artifact.
    """
    scenario_id = scenario.get("id")
    context = scenario.get("context")
    expected_verdict = scenario.get("expected_verdict")
    expected_rules = scenario.get("expected_deciding_rules")
    if not isinstance(scenario_id, str) or not isinstance(context, Mapping):
        raise ScenarioError("scenario requires string id and object context")
    if not isinstance(expected_verdict, str):
        raise ScenarioError("scenario requires string expected_verdict")
    if expected_rules is not None and (
        not isinstance(expected_rules, Sequence)
        or isinstance(expected_rules, str)
        or not all(isinstance(rule_id, str) for rule_id in expected_rules)
    ):
        raise ScenarioError("expected_deciding_rules must be an array of strings")
    verdict = evaluate(context, rulesets)
    return ScenarioResult(
        scenario_id=scenario_id,
        expected_verdict=expected_verdict,
        actual_verdict=verdict.value.value,
        expected_deciding_rules=tuple(expected_rules) if expected_rules is not None else None,
        actual_deciding_rules=verdict.deciding_rules,
        verdict=verdict,
    )
