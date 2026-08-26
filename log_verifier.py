"""Dependency-free public verifier for RFC 6962-style inclusion proofs."""

from __future__ import annotations

import hashlib


def verify_inclusion(
    leaf: bytes, index: int, tree_size: int, proof: tuple[bytes, ...], expected_root: bytes
) -> bool:
    """Verify an audit path without importing the Statuta package."""
    if not 0 <= index < tree_size:
        return False
    proof_index = 0

    def rebuild(local_index: int, size: int) -> bytes:
        nonlocal proof_index
        if size == 1:
            return hashlib.sha256(b"\x00" + leaf).digest()
        split = 1 << (size.bit_length() - 2)
        if local_index < split:
            left = rebuild(local_index, split)
            sibling = proof[proof_index]
            proof_index += 1
            return hashlib.sha256(b"\x01" + left + sibling).digest()
        right = rebuild(local_index - split, size - split)
        sibling = proof[proof_index]
        proof_index += 1
        return hashlib.sha256(b"\x01" + sibling + right).digest()

    try:
        return rebuild(index, tree_size) == expected_root and proof_index == len(proof)
    except IndexError:
        return False
