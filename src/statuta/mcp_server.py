"""Read-only stdio MCP server exposing Statuta's public catalog tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

from statuta.mcp import call_tool

_CATALOG_PATH = Path("corpus/catalog.json")
server = MCPServer(
    name="statuta",
    title="Statuta",
    description=(
        "Read-only statutory research tools. Not legal advice or a compliance certification."
    ),
)


def _catalog() -> dict[str, Any]:
    return json.loads(_CATALOG_PATH.read_text())


@server.tool(description="List jurisdiction artifacts and explicit coverage status.")
def list_jurisdictions() -> dict[str, Any]:
    return dict(call_tool("list_jurisdictions", {}, _catalog()))


@server.tool(description="Retrieve explicit coverage information for one jurisdiction.")
def get_coverage(jurisdiction: str) -> dict[str, Any]:
    return dict(call_tool("get_coverage", {"jurisdiction": jurisdiction}, _catalog()))


@server.tool(description="Search cited statutory passages. It cannot answer legality questions.")
def search_statute(query: str, passages: list[dict[str, str]]) -> dict[str, Any]:
    return dict(call_tool("search_statute", {"query": query, "passages": passages}, _catalog()))


@server.tool(description="Return a deterministic evaluator status without paraphrasing it.")
def evaluate_query() -> dict[str, Any]:
    return dict(call_tool("evaluate_query", {}, _catalog()))


def main() -> None:
    """Run the stdio MCP transport."""
    server.run()
