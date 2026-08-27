"""Local cited retrieval index tests."""

from pathlib import Path

from statuta.index import index_passages, query


def test_sqlite_fts_index_returns_cited_passages(tmp_path: Path) -> None:
    path = tmp_path / "passages.sqlite"
    index_passages(
        path, [{"citation": "Synthetic § 1", "text": "Retention is limited to twenty-one days."}]
    )
    assert query(path, "Retention")[0]["citation"] == "Synthetic § 1"
