"""Tests for published Phase 2 L3 reporting metrics."""

from statuta.reporting import VerdictObservation, verdict_metrics


def test_l3_report_distinguishes_permissive_and_silence_errors() -> None:
    result = verdict_metrics(
        [
            VerdictObservation("prohibited", "unregulated", "boundary"),
            VerdictObservation("prohibited", "indeterminate", "missing_field"),
            VerdictObservation("permitted", "prohibited", "clear"),
            VerdictObservation("permitted", "permitted", "clear"),
        ]
    )
    assert result["verdict_accuracy"] == 0.25
    assert result["permissive_error_rate"] == 0.25
    assert result["silence_error_rate"] == 0.25
    assert result["restrictive_error_rate"] == 0.25
