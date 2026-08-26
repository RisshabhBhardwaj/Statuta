"""Immutable corpus-catalog contracts and release-readiness checks."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class CorpusError(ValueError):
    """Raised when a corpus catalog makes an unsafe release claim."""


def validate_catalog(catalog: Mapping[str, Any]) -> None:
    """Ensure every jurisdiction has one explicit non-silent coverage status."""
    entries = catalog.get("jurisdictions")
    if not isinstance(entries, Sequence) or isinstance(entries, str):
        raise CorpusError("catalog jurisdictions must be an array")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise CorpusError("catalog entries must be objects")
        code = entry.get("code")
        status = entry.get("status")
        if not isinstance(code, str) or code in seen:
            raise CorpusError("catalog jurisdiction codes must be unique strings")
        if status not in {"candidate_unreviewed", "released", "absent_ruleset", "coverage_pending"}:
            raise CorpusError("catalog status is not recognized")
        if status == "released" and not isinstance(entry.get("ruleset_path"), str):
            raise CorpusError("released catalog entry requires a ruleset_path")
        if status == "absent_ruleset" and not isinstance(entry.get("basis"), str):
            raise CorpusError("absent ruleset requires a documented basis")
        seen.add(code)


def released_ruleset_paths(catalog: Mapping[str, Any]) -> tuple[str, ...]:
    """Return only explicitly released artifact paths, never candidate paths."""
    validate_catalog(catalog)
    return tuple(
        entry["ruleset_path"] for entry in catalog["jurisdictions"] if entry["status"] == "released"
    )
