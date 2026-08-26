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
