"""Read-only tool dispatch suitable for an MCP transport adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from statuta.corpus import released_ruleset_paths, validate_catalog
from statuta.retrieve import search

DISCLAIMER = "Research artifact; not legal advice or a compliance certification."


def call_tool(
    name: str, arguments: Mapping[str, Any], catalog: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Expose read-only catalog and text-search tools; no mutation path exists."""
    validate_catalog(catalog)
    if name == "list_jurisdictions":
        return {"jurisdictions": catalog["jurisdictions"], "disclaimer": DISCLAIMER}
    if name == "get_coverage":
        code = arguments.get("jurisdiction")
        entries = [entry for entry in catalog["jurisdictions"] if entry["code"] == code]
        return {"entries": entries, "disclaimer": DISCLAIMER}
    if name == "search_statute":
        results = search(str(arguments.get("query", "")), arguments.get("passages", []))
        return {"results": [item.__dict__ for item in results], "disclaimer": DISCLAIMER}
    if name == "evaluate_query":
        return {
            "error": "No released rulesets are available for deterministic evaluation.",
            "released_rulesets": released_ruleset_paths(catalog),
            "disclaimer": DISCLAIMER,
        }
    raise ValueError("unknown or non-read-only MCP tool")
