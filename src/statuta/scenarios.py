"""Seeded, content-free fixtures for evaluator testing."""

from __future__ import annotations

import random
from typing import Any


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
