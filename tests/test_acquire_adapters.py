"""Offline acquisition-adapter tests."""

from pathlib import Path

from statuta.acquire import FileSourceAdapter


def test_file_adapter_reads_caller_selected_source(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("Public statutory text")
    assert FileSourceAdapter(source).fetch_text() == "Public statutory text"
