from __future__ import annotations

import pandas as pd
import pytest

from portfolio_backtester.tca_calibration import calibrate_cost_model


def _observations() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "trade_date": ["2026-01-02", "2026-01-03"],
            "requested_notional": [100_000.0, 300_000.0],
            "filled_notional": [100_000.0, 150_000.0],
            "modeled_cost_bps": [10.0, 20.0],
            "realized_cost_bps": [14.0, 30.0],
        }
    )


def test_calibration_weights_costs_by_requested_notional_and_reports_coverage() -> None:
    receipt = calibrate_cost_model(
        _observations(),
        model_version="cost-model.v1",
        source_version="tca.2026-01",
        min_observations=2,
    )

    assert receipt.status == "ready"
    assert receipt.observation_count == 2
    assert receipt.coverage_ratio == pytest.approx(0.625)
    assert receipt.modeled_cost_bps == pytest.approx(17.5)
    assert receipt.realized_cost_bps == pytest.approx(26.0)
    assert receipt.residual_cost_bps == pytest.approx(8.5)
    assert receipt.recommended_cost_bps == pytest.approx(26.0)
    assert receipt.to_mapping()["schema_version"] == "portfolio_backtester.tca-calibration.v1"


def test_calibration_does_not_promote_incomplete_or_small_sample() -> None:
    receipt = calibrate_cost_model(
        _observations(),
        model_version="cost-model.v1",
        source_version="tca.2026-01",
        min_observations=3,
    )

    assert receipt.status == "insufficient_data"
    assert receipt.recommended_cost_bps is None


def test_calibration_rejects_missing_or_invalid_observations() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        calibrate_cost_model(
            _observations().drop(columns=["realized_cost_bps"]),
            model_version="cost-model.v1",
            source_version="tca.2026-01",
        )

    invalid = _observations()
    invalid.loc[0, "requested_notional"] = 0.0
    with pytest.raises(ValueError, match="requested_notional must be positive"):
        calibrate_cost_model(
            invalid,
            model_version="cost-model.v1",
            source_version="tca.2026-01",
        )
