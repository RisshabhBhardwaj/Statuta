"""Stable, offset-preserving statutory numbering segmentation."""

from __future__ import annotations

import re
from dataclasses import dataclass

_HEADING = re.compile(r"(?m)^(?:§\s*[^\n]+|[A-Z]\.\s|\([0-9A-Za-z]+\)\s)")
_DEFINITION = re.compile(
    r'(?m)^\s*(?:[A-Z]\.\s*)?"([^"]+)"\s+means\s+(.+?)(?=\n\s*(?:[A-Z]\.\s*)?"|\Z)',
    re.DOTALL,
)


@dataclass(frozen=True)
class Provision:
    """A stable source slice suitable for grounding and proposal."""

    id: str
    start: int
    end: int
    text: str
    family_id: str


def segment(text: str, *, source_id: str) -> tuple[Provision, ...]:
    """Split on statutory-looking headings; retain exact source offsets."""
    matches = list(_HEADING.finditer(text))
    if not matches:
        return (Provision(f"{source_id}:0", 0, len(text), text, f"{source_id}:0"),) if text else ()
    provisions: list[Provision] = []
    current_section = f"{source_id}:0"
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        heading = match.group().strip().replace("\n", " ")
        provision_id = f"{source_id}:{heading.rstrip('.')}"
        if heading.startswith("§"):
            current_section = provision_id
        family = current_section if re.match(r"^[A-Z]\.$", heading) else provision_id
        if "(" in provision_id:
            family = provision_id.rsplit("(", 1)[0].rstrip()
        provisions.append(
            Provision(provision_id, match.start(), end, text[match.start() : end], family)
        )
    return tuple(provisions)


def extract_definitions(provisions: tuple[Provision, ...]) -> dict[str, str]:
    """Extract quoted ``term means definition`` pairs before rule proposal."""
    definitions: dict[str, str] = {}
    for provision in provisions:
        if "means" not in provision.text.lower():
            continue
        for match in _DEFINITION.finditer(provision.text):
            definitions[match.group(1)] = match.group(2).strip()
    return definitions
