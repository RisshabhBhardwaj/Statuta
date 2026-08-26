"""Merkle and commitment invariants."""

from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from hypothesis import given
from hypothesis import strategies as st

from statuta.log.checkpoints import (
    countersign_checkpoint,
    sign_checkpoint,
    verify_checkpoint,
    verify_countersignature,
)
from statuta.log.commitments import commitment
from statuta.log.merkle import MerkleTree
from statuta.log.storage import append_leaf, read_leaves
from statuta.log_verifier import verify_consistency, verify_inclusion


@given(st.lists(st.binary(min_size=1, max_size=12), min_size=1, max_size=16))
def test_every_inclusion_proof_verifies(leaves: list[bytes]) -> None:
    tree = MerkleTree(tuple(leaves))
    for index, leaf in enumerate(leaves):
        assert verify_inclusion(
            leaf, index, len(leaves), tree.inclusion_proof(index), tree.root_hash
        )


def test_mutated_leaf_and_epoch_rotation_fail_to_link() -> None:
    tree = MerkleTree((b"one", b"two", b"three"))
    assert not verify_inclusion(b"tampered", 1, 3, tree.inclusion_proof(1), tree.root_hash)
    assert commitment(b"secret", "2026-Q3", b"opaque") != commitment(
        b"secret", "2026-Q4", b"opaque"
    )


def test_signed_checkpoint_rejects_tampering() -> None:
    private_key = Ed25519PrivateKey.generate()
    checkpoint = {"tree_size": 3, "root_hash": "abc", "timestamp": "2026-08-26T00:00:00Z"}
    signature = sign_checkpoint(private_key, checkpoint)
    assert verify_checkpoint(private_key.public_key(), checkpoint, signature)
    assert not verify_checkpoint(
        private_key.public_key(), {**checkpoint, "tree_size": 4}, signature
    )


def test_witness_countersignature_and_consistency_proof() -> None:
    operator, witness = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    signature = sign_checkpoint(operator, {"tree_size": 3})
    assert verify_countersignature(
        witness.public_key(), signature, countersign_checkpoint(witness, signature)
    )
    tree = MerkleTree((b"one", b"two", b"three"))
    old = MerkleTree((b"one", b"two"))
    assert verify_consistency(2, 3, old.root_hash, tree.root_hash, tree.consistency_proof(2))


@given(st.lists(st.binary(min_size=1, max_size=8), min_size=2, max_size=10))
def test_every_prefix_consistency_proof_verifies(leaves: list[bytes]) -> None:
    tree = MerkleTree(tuple(leaves))
    for old_size in range(1, len(leaves)):
        old = MerkleTree(tuple(leaves[:old_size]))
        assert verify_consistency(
            old_size, len(leaves), old.root_hash, tree.root_hash, tree.consistency_proof(old_size)
        )


def test_append_only_storage_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "leaves.jsonl"
    assert append_leaf(path, b"one") == 0
    assert append_leaf(path, b"two") == 1
    assert read_leaves(path) == (b"one", b"two")
