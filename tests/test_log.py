"""Merkle and commitment invariants."""

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from hypothesis import given
from hypothesis import strategies as st

from statuta.log.checkpoints import sign_checkpoint, verify_checkpoint
from statuta.log.commitments import commitment
from statuta.log.merkle import MerkleTree
from statuta.log_verifier import verify_inclusion


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
