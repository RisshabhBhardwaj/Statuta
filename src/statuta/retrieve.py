"""Read-only text retrieval with a hard legality-conclusion refusal boundary."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

LEGALITY_TERMS = ("lawful", "legal", "allowed", "permitted", "prohibited", "compliant")


@dataclass(frozen=True)
class SearchResult:
    citation: str
    text: str
    score: int


def search(query: str, passages: Sequence[Mapping[str, str]]) -> tuple[SearchResult, ...]:
    """Search supplied public passages, refusing legal-conclusion questions."""
    if any(term in query.lower() for term in LEGALITY_TERMS):
        raise ValueError(
            "Retrieval cannot answer legality questions; use evaluate_query with context."
        )
    terms = set(query.lower().split())
    results = [
        SearchResult(item["citation"], item["text"], len(terms & set(item["text"].lower().split())))
        for item in passages
        if "citation" in item and "text" in item
    ]
    return tuple(sorted((item for item in results if item.score), key=lambda item: -item.score))
