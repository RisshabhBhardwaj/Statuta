"""Portable recorded-provider artifacts and deterministic replay."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def write_artifact(
    path: Path, request: Mapping[str, Any], response: Sequence[Mapping[str, Any]]
) -> None:
    """Persist a provider-neutral request/response artifact for offline replay."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"request": request, "response": list(response)}, indent=2) + "\n")


def replay_artifact(path: Path) -> tuple[Mapping[str, Any], tuple[Mapping[str, Any], ...]]:
    """Load a recorded response without network or model access."""
    artifact = json.loads(path.read_text())
    if not isinstance(artifact.get("request"), Mapping) or not isinstance(
        artifact.get("response"), list
    ):
        raise ValueError("invalid proposal artifact")
    return artifact["request"], tuple(artifact["response"])
