from datetime import UTC, datetime

import pytest
from research_contracts.research_run_manifest import ResearchRunManifest


def _payload(tier: str = "diagnostic") -> dict:
    digest = "a" * 64
    return {
        "schema_version": "research.backtest-run.v1",
        "run_id": "r1",
        "strategy_ref": "s",
        "research_purpose": "test",
        "evidence_tier": tier,
        "clock": {
            "schema_version": "research.clock.v1",
            "timezone": "UTC",
            "information_cutoff_at": "2020-01-01T08:00:00+00:00",
            "signal_at": "2020-01-01T08:30:00+00:00",
            "decision_at": "2020-01-01T09:00:00+00:00",
            "earliest_order_at": "2020-01-01T09:30:00+00:00",
            "execution_window_start_at": "2020-01-01T09:30:00+00:00",
            "execution_window_end_at": "2020-01-01T16:00:00+00:00",
            "valuation_at": "2020-01-01T16:00:00+00:00",
            "timing_policy_id": "t",
            "trading_calendar_ref": "cal",
        },
        "configuration_sha256": digest,
        "producer_versions": [{"repository": "q", "commit": "c"}],
        "data_refs": [{"artifact_id": "d", "sha256": digest}],
        "signal_refs": [],
        "portfolio_result_ref": {"artifact_id": "p", "sha256": digest},
        "created_at": datetime.now(UTC).isoformat(),
        "evidence_refs": [],
    }


def test_provenance_round_trip() -> None:
    payload = _payload("execution_aware")
    payload["provenance"] = dict.fromkeys(
        (
            "data_vintage",
            "calendar_version",
            "strategy_version",
            "engine_version",
            "execution_policy",
            "cost_model",
            "random_seed",
        ),
        "v",
    )
    manifest = ResearchRunManifest.from_mapping(payload)
    assert manifest.to_mapping()["provenance"]["data_vintage"] == "v"


def test_execution_manifest_requires_provenance() -> None:
    with pytest.raises(ValueError, match="provenance"):
        ResearchRunManifest.from_mapping(_payload("execution_aware"))
