"""MCP transport tool tests without starting a stdio server."""

import json
from pathlib import Path

from statuta import mcp_server


def test_mcp_tools_read_a_pre_release_catalog(tmp_path: Path, monkeypatch: object) -> None:
    path = tmp_path / "catalog.json"
    path.write_text(
        json.dumps(
            {
                "status": "pre-release",
                "jurisdictions": [{"code": "US-AA", "status": "coverage_pending"}],
            }
        )
    )
    monkeypatch.setattr(mcp_server, "_CATALOG_PATH", path)
    assert mcp_server.list_jurisdictions()["jurisdictions"][0]["code"] == "US-AA"
    assert mcp_server.get_coverage("US-AA")["entries"]
    assert "released rulesets" in mcp_server.evaluate_query()["error"]


def test_mcp_text_search_returns_citations(tmp_path: Path, monkeypatch: object) -> None:
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps({"status": "pre-release", "jurisdictions": []}))
    monkeypatch.setattr(mcp_server, "_CATALOG_PATH", path)
    result = mcp_server.search_statute(
        "retention", [{"citation": "§ 1", "text": "retention limit"}]
    )
    assert result["results"][0]["citation"] == "§ 1"
