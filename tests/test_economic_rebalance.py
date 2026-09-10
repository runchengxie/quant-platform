from __future__ import annotations

import pandas as pd
import pytest

from portfolio_backtester.economic_rebalance import apply_no_trade_band


def _weights(a: float, b: float) -> pd.Series:
    return pd.Series({"A": a, "B": b}, dtype=float)


def test_no_trade_band_keeps_previous_at_or_below_threshold() -> None:
    previous = _weights(0.50, 0.50)
    target = _weights(0.56, 0.44)

    result = apply_no_trade_band(target, previous, min_turnover=0.06)

    assert result.weights.to_dict() == previous.to_dict()
    assert result.diagnostics["method"] == "no_trade_band"
    assert result.diagnostics["min_turnover"] == pytest.approx(0.06)
    assert result.diagnostics["turnover_before"] == pytest.approx(0.06)
    assert result.diagnostics["turnover_after"] == 0.0
    assert result.diagnostics["traded"] is False
    assert result.diagnostics["previous_weights_missing"] is False


def test_no_trade_band_uses_target_above_threshold_without_mutation() -> None:
    previous = _weights(0.50, 0.50)
    target = _weights(0.57, 0.43)
    previous_before = previous.copy()
    target_before = target.copy()

    result = apply_no_trade_band(target, previous, min_turnover=0.06)

    assert result.weights.to_dict() == target.to_dict()
    assert result.diagnostics["turnover_before"] == pytest.approx(0.07)
    assert result.diagnostics["turnover_after"] == pytest.approx(0.07)
    assert result.diagnostics["traded"] is True
    pd.testing.assert_series_equal(previous, previous_before)
    pd.testing.assert_series_equal(target, target_before)


def test_no_trade_band_adopts_target_without_previous_weights() -> None:
    target = _weights(0.60, 0.40)

    result = apply_no_trade_band(target, None, min_turnover=0.10)

    assert result.weights.to_dict() == target.to_dict()
    assert result.diagnostics["previous_weights_missing"] is True
    assert result.diagnostics["turnover_before"] is None
    assert result.diagnostics["turnover_after"] == pytest.approx(0.0)
    assert result.diagnostics["traded"] is True


@pytest.mark.parametrize(
    ("target", "previous", "threshold", "message"),
    [
        (_weights(0.60, 0.40), _weights(0.5, 0.4), 0.1, "sum to 1"),
        (_weights(-0.1, 1.1), _weights(0.5, 0.5), 0.1, "non-negative"),
        (_weights(0.6, 0.4), _weights(0.5, 0.5).rename({"B": "C"}), 0.1, "same assets"),
        (_weights(0.6, 0.4), _weights(0.5, 0.5), -0.1, "min_turnover"),
    ],
)
def test_no_trade_band_rejects_invalid_inputs(
    target: pd.Series,
    previous: pd.Series,
    threshold: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        apply_no_trade_band(target, previous, min_turnover=threshold)
