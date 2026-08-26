"""Reproducible, dependency-light Phase 2 evaluation metrics."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class VerdictObservation:
    """One pre-labeled L3 scenario result."""

    expected: str
    actual: str
    scenario_class: str


def verdict_metrics(observations: Iterable[VerdictObservation]) -> Mapping[str, object]:
    """Compute L3 accuracy, confusion matrix, and asymmetric error rates."""
    rows = tuple(observations)
    total = len(rows)
    confusion = Counter((row.expected, row.actual) for row in rows)
    correct = sum(row.expected == row.actual for row in rows)
    permissive = sum(
        row.expected == "prohibited" and row.actual in {"permitted", "unregulated"} for row in rows
    )
    restrictive = sum(row.expected == "permitted" and row.actual == "prohibited" for row in rows)
    silence = sum(row.expected == "prohibited" and row.actual == "indeterminate" for row in rows)
    by_class = {
        category: sum(row.expected == row.actual for row in rows if row.scenario_class == category)
        / count
        for category in {row.scenario_class for row in rows}
        if (count := sum(row.scenario_class == category for row in rows))
    }
    return {
        "scenario_count": total,
        "verdict_accuracy": correct / total if total else None,
        "permissive_error_rate": permissive / total if total else None,
        "restrictive_error_rate": restrictive / total if total else None,
        "silence_error_rate": silence / total if total else None,
        "accuracy_by_scenario_class": by_class,
        "confusion_matrix": {
            f"{expected}->{actual}": count
            for (expected, actual), count in sorted(confusion.items())
        },
    }
