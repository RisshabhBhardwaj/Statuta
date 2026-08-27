"""Tests for reproducible content-free scenario generation."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from statuta.scenarios import generate_contexts, generate_gold_suite


@given(seed=st.integers(), count=st.integers(min_value=0, max_value=50))
def test_generation_is_reproducible_and_bounded(seed: int, count: int) -> None:
    contexts = generate_contexts(seed, count)
    assert contexts == generate_contexts(seed, count)
    assert len(contexts) == count
    assert all(0 <= item["record"]["age_days"] <= 60 for item in contexts)
    assert all("target_ref" not in item for item in contexts)


def test_gold_suite_is_reproducible_and_spans_all_required_classes() -> None:
    suite = generate_gold_suite(1)
    assert len(suite) == 150
    assert suite == generate_gold_suite(1)
    assert {item["scenario_class"] for item in suite} == {
        "clear",
        "boundary",
        "missing_field",
        "cross_jurisdiction",
        "unregulated",
    }
