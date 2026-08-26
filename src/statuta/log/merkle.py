"""RFC 6962 domain-separated Merkle hashing and inclusion proofs."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


def _leaf(data: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + data).digest()


def _node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def root_hash(leaves: tuple[bytes, ...]) -> bytes:
    """Return the RFC 6962 tree hash for a non-empty ordered leaf sequence."""
    if not leaves:
        return hashlib.sha256(b"").digest()
    if len(leaves) == 1:
        return _leaf(leaves[0])
    split = 1 << ((len(leaves) - 1).bit_length() - 1)
    return _node(root_hash(leaves[:split]), root_hash(leaves[split:]))


def inclusion_proof(leaves: tuple[bytes, ...], index: int) -> tuple[bytes, ...]:
    """Create an RFC 6962 audit path for ``leaves[index]``."""
    if not 0 <= index < len(leaves):
        raise IndexError("leaf index is outside the tree")
    if len(leaves) == 1:
        return ()
    split = 1 << ((len(leaves) - 1).bit_length() - 1)
    if index < split:
        return inclusion_proof(leaves[:split], index) + (root_hash(leaves[split:]),)
    return inclusion_proof(leaves[split:], index - split) + (root_hash(leaves[:split]),)


def consistency_proof(leaves: tuple[bytes, ...], old_size: int) -> tuple[bytes, ...]:
    """Build an RFC 6962 consistency proof for a non-empty prefix."""
    if not 0 < old_size <= len(leaves):
        raise ValueError("old size must be within current tree")

    def build(items: tuple[bytes, ...], size: int, include_root: bool) -> tuple[bytes, ...]:
        if size == len(items):
            return () if include_root else (root_hash(items),)
        split = 1 << ((len(items) - 1).bit_length() - 1)
        if size <= split:
            return build(items[:split], size, include_root) + (root_hash(items[split:]),)
        return build(items[split:], size - split, False) + (root_hash(items[:split]),)

    return build(leaves, old_size, True)


@dataclass(frozen=True)
class MerkleTree:
    """An immutable in-memory tree; storage is intentionally caller-owned."""

    leaves: tuple[bytes, ...]

    @property
    def root_hash(self) -> bytes:
        return root_hash(self.leaves)

    def append(self, data: bytes) -> MerkleTree:
        """Return a new tree without mutating prior append-only history."""
        return MerkleTree((*self.leaves, data))

    def inclusion_proof(self, index: int) -> tuple[bytes, ...]:
        return inclusion_proof(self.leaves, index)

    def consistency_proof(self, old_size: int) -> tuple[bytes, ...]:
        return consistency_proof(self.leaves, old_size)
