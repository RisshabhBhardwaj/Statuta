"""Tests for deterministic statutory segmentation and definitions."""

from statuta.segment import extract_definitions, segment


def test_segment_preserves_offsets_and_families() -> None:
    text = '§ 1. Scope\nA. "System" means a data service.\nB. Data shall be deleted.\n'
    provisions = segment(text, source_id="US-AA-1")
    assert len(provisions) == 3
    assert all(text[item.start : item.end] == item.text for item in provisions)
    assert provisions[1].family_id == provisions[2].family_id
    assert extract_definitions(provisions) == {"System": "a data service."}
