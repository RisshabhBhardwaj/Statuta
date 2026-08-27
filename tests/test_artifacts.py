"""Recorded provider response replay tests."""

from pathlib import Path

from statuta.compile.artifacts import replay_artifact, write_artifact


def test_provider_artifacts_replay_without_network(tmp_path: Path) -> None:
    path = tmp_path / "proposal.json"
    write_artifact(path, {"model": "fixture-a"}, [{"effect": "prohibited"}])
    assert replay_artifact(path) == ({"model": "fixture-a"}, ({"effect": "prohibited"},))
