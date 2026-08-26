"""Dependency-free public verifier for RFC 6962-style inclusion proofs."""

from __future__ import annotations

import hashlib


def verify_inclusion(
    leaf: bytes, index: int, tree_size: int, proof: tuple[bytes, ...], expected_root: bytes
) -> bool:
    """Verify an audit path without importing the rest of the package."""
    if not 0 <= index < tree_size:
        return False
    proof_index = 0

    def rebuild(local_index: int, size: int) -> bytes:
        nonlocal proof_index
        if size == 1:
            return hashlib.sha256(b"\x00" + leaf).digest()
        split = 1 << ((size - 1).bit_length() - 1)
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


def verify_consistency(
    old_size: int, new_size: int, old_root: bytes, new_root: bytes, proof: tuple[bytes, ...]
) -> bool:
    """Verify a standard RFC 6962 consistency proof."""
    if not 0 < old_size <= new_size:
        return False
    if old_size == new_size:
        return old_root == new_root and not proof
    fn, sn = old_size - 1, new_size - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1
    if not proof:
        return False
    if fn == 0:
        fr, sr, rest = old_root, old_root, proof
    else:
        first, *rest = proof
        fr = sr = first
    for item in rest:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            fr = hashlib.sha256(b"\x01" + item + fr).digest()
            sr = hashlib.sha256(b"\x01" + item + sr).digest()
            while not (fn & 1) and fn:
                fn >>= 1
                sn >>= 1
        else:
            sr = hashlib.sha256(b"\x01" + sr + item).digest()
        fn >>= 1
        sn >>= 1
    return fr == old_root and sr == new_root
