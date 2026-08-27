"""Provider adapter protocol and ablation manifest contracts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol


class StructuredProvider(Protocol):
    """A provider that returns schema-shaped proposals for an explicit request."""

    name: str

    def propose(self, request: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]: ...


@dataclass(frozen=True)
class Ablation:
    """One declared pipeline configuration for a reproducible evaluation report."""

    name: str
    disabled_gates: tuple[str, ...]


DEFAULT_ABLATIONS = (Ablation("full_pipeline", ()), Ablation("without_G2", ("G2_grounding",)))
