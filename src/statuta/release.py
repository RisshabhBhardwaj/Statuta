"""Release-package verification for immutable public corpus artifacts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from statuta.core.validation import validate_ruleset


def package_release(ruleset: Mapping[str, Any], destination: Path) -> str:
    """Validate and write a canonical immutable release artifact, returning its digest."""
    if ruleset.get("artifact_status") != "released":
        raise ValueError("only released rulesets may be packaged")
    validate_ruleset(ruleset)
    encoded = json.dumps(ruleset, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() != encoded:
        raise ValueError("immutable release path already contains different content")
    destination.write_bytes(encoded)
    return digest
