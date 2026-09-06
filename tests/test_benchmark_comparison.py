import numpy as np
import pandas as pd
import pytest

from portfolio_backtester.benchmark_comparison import compare_portfolio_returns


def test_compare_portfolio_returns_reports_active_metrics() -> None:
    portfolio = pd.Series([0.02, 0.00, 0.01], index=pd.date_range("2024-01-01", periods=3))
    benchmark = pd.Series([0.01, 0.00, 0.00], index=portfolio.index)
    weights = pd.Series({"A": 0.7, "B": 0.3})
    benchmark_weights = pd.Series({"A": 0.5, "B": 0.5})

    result = compare_portfolio_returns(portfolio, benchmark, weights, benchmark_weights)

    assert result["portfolio_total_return"] == pytest.approx(0.0302)
    assert result["benchmark_total_return"] == pytest.approx(0.0100)
    assert result["excess_total_return"] == pytest.approx(0.0200)
    assert result["active_share"] == pytest.approx(0.2)
    assert result["turnover"] == pytest.approx(0.0)
    assert result["tracking_error"] > 0


def test_compare_portfolio_returns_handles_zero_excess_volatility() -> None:
    returns = pd.Series([0.01, 0.01], index=pd.date_range("2024-01-01", periods=2))
    weights = pd.Series({"A": 1.0})

    result = compare_portfolio_returns(returns, returns, weights, weights)

    assert np.isnan(result["information_ratio"])
    assert result["tracking_error"] == pytest.approx(0.0)
    assert result["active_share"] == pytest.approx(0.0)


def test_compare_portfolio_returns_uses_previous_weights_for_turnover() -> None:
    returns = pd.Series([0.01])
    result = compare_portfolio_returns(
        returns,
        returns,
        pd.Series({"A": 0.7, "B": 0.3}),
        pd.Series({"A": 0.5, "B": 0.5}),
        previous_weights=pd.Series({"A": 0.5, "B": 0.5}),
    )

    assert result["turnover"] == pytest.approx(0.2)


def test_compare_portfolio_returns_rejects_misaligned_inputs() -> None:
    with pytest.raises(ValueError, match="returns"):
        compare_portfolio_returns(
            pd.Series([0.1]),
            pd.Series([0.1, 0.2]),
            pd.Series({"A": 1.0}),
            pd.Series({"A": 1.0}),
        )
