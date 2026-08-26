"""Mechanical, model-independent gates applied before human review."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from statuta.core.grounding import GroundingError, verify_grounding
from statuta.core.validation import SemanticValidationError, _validate_predicate


@dataclass(frozen=True)
class GateResult:
    """Disposition of one candidate after deterministic checks."""

    accepted: bool
    discarded_by: tuple[str, ...]
    review_flags: tuple[str, ...]


def structurally_equivalent(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    """Compare the fields that define proposal equivalence, never prose similarity."""
    keys = ("rule_type", "effect", "applies_when", "condition", "requirements", "obligations")
    return all(left.get(key) == right.get(key) for key in keys)


def gate_candidate(
    candidate: Mapping[str, Any], provision_text: str, *, family_text: str = ""
) -> GateResult:
    """Run G2–G9 equivalents; fatal defects are discarded, ambiguity is flagged."""
    fatal: list[str] = []
    flags: list[str] = []
    try:
        verify_grounding(candidate, provision_text)
    except (GroundingError, KeyError, TypeError):
        fatal.extend(("G2_grounding", "G3_span"))
    for predicate_key in ("applies_when", "condition"):
        try:
            _validate_predicate(candidate.get(predicate_key), predicate_key)
        except SemanticValidationError:
            fatal.extend(("G4_field_path", "G5_operator"))
    numbers = re.findall(r"\d+", repr(candidate))
    if any(
        number not in provision_text and number not in _spelled_numbers(provision_text)
        for number in numbers
    ):
        flags.append("G7_numeric_sanity")
    exception_words = ("except", "unless", "provided that", "notwithstanding")
    if any(word in family_text.lower() for word in exception_words) and not candidate.get(
        "exceptions"
    ):
        flags.append("G8_family_completeness")
    return GateResult(not fatal, tuple(sorted(set(fatal))), tuple(sorted(set(flags))))


def _spelled_numbers(text: str) -> set[str]:
    words = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "ten": "10",
        "fourteen": "14",
        "twenty": "20",
        "twenty-one": "21",
        "thirty": "30",
    }
    lower = text.lower()
    return {digit for word, digit in words.items() if word in lower}
