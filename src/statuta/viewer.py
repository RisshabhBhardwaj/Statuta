"""Static, data-only corpus viewer generation."""

from __future__ import annotations

import html
from collections.abc import Mapping
from typing import Any


def render_catalog(catalog: Mapping[str, Any]) -> str:
    """Render a static pre-release/released catalog with no evaluation controls."""
    rows = "".join(
        "<li><code>"
        f"{html.escape(str(entry['code']))}</code>: {html.escape(str(entry['status']))}</li>"
        for entry in catalog.get("jurisdictions", [])
    )
    return (
        "<!doctype html><title>Statuta corpus</title><h1>Statuta corpus</h1>"
        "<p>Research artifact; not legal advice or a compliance certification.</p>"
        f"<p>Status: {html.escape(str(catalog.get('status')))}</p><ul>{rows}</ul>"
    )
