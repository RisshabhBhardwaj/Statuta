"""Ed25519 signed tree-head checkpoints."""

from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def sign_checkpoint(private_key: Ed25519PrivateKey, checkpoint: Mapping[str, Any]) -> str:
    """Sign canonical public checkpoint JSON and return a base64 signature."""
    payload = json.dumps(checkpoint, sort_keys=True, separators=(",", ":")).encode()
    return base64.b64encode(private_key.sign(payload)).decode()


def verify_checkpoint(
    public_key: Ed25519PublicKey, checkpoint: Mapping[str, Any], signature: str
) -> bool:
    """Verify an Ed25519 checkpoint signature without ambient state."""
    payload = json.dumps(checkpoint, sort_keys=True, separators=(",", ":")).encode()
    try:
        public_key.verify(base64.b64decode(signature), payload)
    except Exception:
        return False
    return True


def countersign_checkpoint(private_key: Ed25519PrivateKey, checkpoint_signature: str) -> str:
    """Create a witness signature over the operator's checkpoint signature."""
    return base64.b64encode(private_key.sign(checkpoint_signature.encode())).decode()


def verify_countersignature(
    public_key: Ed25519PublicKey, checkpoint_signature: str, witness_signature: str
) -> bool:
    """Verify a witness's independent attestation of the exact checkpoint signature."""
    try:
        public_key.verify(base64.b64decode(witness_signature), checkpoint_signature.encode())
    except Exception:
        return False
    return True
