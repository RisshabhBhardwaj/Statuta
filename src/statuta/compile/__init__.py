"""Compile-plane proposal validation and review triage."""

from statuta.compile.gates import GateResult, gate_candidate, structurally_equivalent
from statuta.compile.proposals import ProposalPair, propose_pair, review_priority

__all__ = [
    "GateResult",
    "ProposalPair",
    "gate_candidate",
    "propose_pair",
    "review_priority",
    "structurally_equivalent",
]
