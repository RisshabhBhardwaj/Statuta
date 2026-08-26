"""Provider-neutral structured proposal records and review prioritization."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from statuta.compile.gates import structurally_equivalent
from statuta.segment import Provision

Proposer = Callable[[Provision, Mapping[str, str]], Sequence[Mapping[str, Any]]]


@dataclass(frozen=True)
class ProposalPair:
    """Two independent proposal outputs retained for reproducibility and triage."""

    provision_id: str
    first_model: str
    second_model: str
    first: tuple[Mapping[str, Any], ...]
    second: tuple[Mapping[str, Any], ...]

    @property
    def agreement(self) -> bool:
        """Whether both model outputs contain the same structural rule multiset."""
        if len(self.first) != len(self.second):
            return False
        unmatched = list(self.second)
        for candidate in self.first:
            for index, other in enumerate(unmatched):
                if structurally_equivalent(candidate, other):
                    unmatched.pop(index)
                    break
            else:
                return False
        return not unmatched


def propose_pair(
    provision: Provision,
    definitions: Mapping[str, str],
    *,
    first_model: str,
    first_proposer: Proposer,
    second_model: str,
    second_proposer: Proposer,
) -> ProposalPair:
    """Call injected providers independently; provider I/O stays outside core code."""
    return ProposalPair(
        provision.id,
        first_model,
        second_model,
        tuple(first_proposer(provision, definitions)),
        tuple(second_proposer(provision, definitions)),
    )


def review_priority(pair: ProposalPair, *, gate_flags: Sequence[str] = ()) -> tuple[int, str]:
    """Return a stable information-gain-first queue priority and explanation."""
    if not pair.agreement:
        return (0, "model disagreement")
    if gate_flags:
        return (1, "mechanical gate review flag")
    if any(item.get("effect") == "prohibited" for item in (*pair.first, *pair.second)):
        return (2, "prohibition candidate")
    if (
        not pair.first
        and not pair.second
        and any(word in pair.provision_id.lower() for word in ("shall", "must"))
    ):
        return (3, "abstention recall audit")
    return (4, "standard review")
