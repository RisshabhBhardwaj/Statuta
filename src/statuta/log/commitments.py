"""Keyed, epoch-scoped commitments for metadata-only log leaves."""

from __future__ import annotations

import hashlib
import hmac


def commitment(secret: bytes, epoch: str, value: bytes) -> str:
    """Return a domain-separated HMAC commitment; never use a plain hash."""
    return (
        "hmac-sha256:"
        + hmac.new(secret, epoch.encode() + b"\x00" + value, hashlib.sha256).hexdigest()
    )
