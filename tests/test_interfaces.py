"""Read-only interface and static-viewer tests."""

from statuta.mcp import call_tool
from statuta.viewer import render_catalog

CATALOG = {
    "status": "pre-release",
    "jurisdictions": [{"code": "US-AA", "status": "coverage_pending"}],
}


def test_mcp_is_read_only_and_returns_disclaimers() -> None:
    assert "disclaimer" in call_tool("list_jurisdictions", {}, CATALOG)
    assert "released rulesets" in call_tool("evaluate_query", {}, CATALOG)["error"]


def test_viewer_has_no_evaluation_form() -> None:
    page = render_catalog(CATALOG)
    assert "US-AA" in page
    assert "<form" not in page
