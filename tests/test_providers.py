"""Provider protocol and ablation manifest tests."""

from statuta.compile.providers import DEFAULT_ABLATIONS


def test_required_no_grounding_ablation_is_declared() -> None:
    assert DEFAULT_ABLATIONS[1].disabled_gates == ("G2_grounding",)
