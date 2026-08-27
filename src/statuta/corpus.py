"""Immutable corpus-catalog contracts and release-readiness checks."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

US_STATE_CODES = (
    "US-AL",
    "US-AK",
    "US-AZ",
    "US-AR",
    "US-CA",
    "US-CO",
    "US-CT",
    "US-DE",
    "US-FL",
    "US-GA",
    "US-HI",
    "US-ID",
    "US-IL",
    "US-IN",
    "US-IA",
    "US-KS",
    "US-KY",
    "US-LA",
    "US-ME",
    "US-MD",
    "US-MA",
    "US-MI",
    "US-MN",
    "US-MS",
    "US-MO",
    "US-MT",
    "US-NE",
    "US-NV",
    "US-NH",
    "US-NJ",
    "US-NM",
    "US-NY",
    "US-NC",
    "US-ND",
    "US-OH",
    "US-OK",
    "US-OR",
    "US-PA",
    "US-RI",
    "US-SC",
    "US-SD",
    "US-TN",
    "US-TX",
    "US-UT",
    "US-VT",
    "US-VA",
    "US-WA",
    "US-WV",
    "US-WI",
    "US-WY",
)


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


def coverage_summary(catalog: Mapping[str, Any]) -> Mapping[str, int]:
    """Count explicit jurisdiction coverage states for public reporting."""
    validate_catalog(catalog)
    summary: dict[str, int] = {}
    for entry in catalog["jurisdictions"]:
        status = entry["status"]
        summary[status] = summary.get(status, 0) + 1
    return summary


def complete_catalog(catalog: Mapping[str, Any]) -> dict[str, Any]:
    """Return all fifty states with unknown coverage recorded explicitly, never implied."""
    validate_catalog(catalog)
    existing = {entry["code"]: dict(entry) for entry in catalog["jurisdictions"]}
    entries = [
        existing.get(code, {"code": code, "status": "coverage_pending"}) for code in US_STATE_CODES
    ]
    return {**catalog, "jurisdictions": entries}
