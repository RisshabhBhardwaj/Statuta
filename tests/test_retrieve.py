"""Retrieval boundary tests."""

import pytest
from statuta.retrieve import search


def test_retrieval_returns_cited_text_but_refuses_legality() -> None:
    passages = [{"citation": "Synthetic § 1", "text": "Data retention is limited."}]
    assert search("retention", passages)[0].citation == "Synthetic § 1"
    with pytest.raises(ValueError, match="cannot answer legality"):
        search("Is this lawful?", passages)
