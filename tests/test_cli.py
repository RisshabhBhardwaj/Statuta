"""CLI smoke tests."""

import sys
from pathlib import Path

from statuta.cli import main
from statuta.scenarios import numeric_boundary_contexts


def test_numeric_boundary_generation() -> None:
    ruleset = {
        "jurisdiction": {"code": "US-AA"},
        "rules": [{"condition": {"field": "record.age_days", "value": 21}}],
    }
    assert [item["record"]["age_days"] for item in numeric_boundary_contexts([ruleset])] == [
        20,
        21,
        22,
    ]


def test_cli_generates_synthetic_contexts(monkeypatch: object, capsys: object) -> None:
    monkeypatch.setattr(
        sys, "argv", ["statuta", "scenarios-generate", "--seed", "1", "--count", "1"]
    )
    main()
    assert "age_days" in capsys.readouterr().out


def test_cli_reports_pre_release_catalog(monkeypatch: object, capsys: object) -> None:
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setattr(
        sys, "argv", ["statuta", "catalog", "--path", str(root / "corpus/catalog.json")]
    )
    main()
    assert '"status": "pre-release"' in capsys.readouterr().out
