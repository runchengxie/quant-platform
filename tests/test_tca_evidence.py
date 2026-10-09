from __future__ import annotations

import importlib
import importlib.util

import pandas as pd
import pytest


def _api():
    assert importlib.util.find_spec("portfolio_backtester.tca_evidence"), "TCA evidence API missing"
    return importlib.import_module("portfolio_backtester.tca_evidence")


def _observations():
    return pd.DataFrame(
        {
            "order_id": ["a", "b"],
            "trade_date": ["2024-01-02", "2024-01-03"],
            "requested_notional": [100.0, 300.0],
            "filled_notional": [100.0, 150.0],
            "execution_cash": [0.05, 0.2],
            "opportunity_cash": [0.0, 0.25],
            "fee_cash": [0.0, 0.0],
            "total_cash": [0.05, 0.45],
            "total_bps": [5.0, 15.0],
            "liquidity": ["liquid", "liquid"],
        }
    )


def test_grouped_summary_reports_weighted_mean_empirical_tail_and_coverage():
    api = _api()
    source = _observations()
    result = api.summarize_tca(
        source, group_cols=["liquidity"], min_observations=2, min_coverage=0.5, seed=7
    )
    row = result["groups"][0]
    assert result["schema_version"] == "portfolio_backtester.tca-evidence.v2"
    assert row["mean_shortfall_bps"] == pytest.approx(12.5)
    assert row["median_shortfall_bps"] == pytest.approx(10.0)
    assert row["p95_shortfall_bps"] == pytest.approx(14.5)
    assert row["coverage_ratio"] == pytest.approx(0.625)
    assert row["status"] == "ready"
    assert row["observation_count"] == 2
    assert row["date_count"] == 2
    assert row["mean_ci_bps"] == [5.0, 15.0]
    assert source.equals(_observations())
    assert result == api.summarize_tca(
        source, group_cols=["liquidity"], min_observations=2, min_coverage=0.5, seed=7
    )


def test_missing_groups_and_zero_fill_remain_accounted():
    api = _api()
    frame = _observations()
    frame.loc[1, "liquidity"] = None
    frame.loc[1, "filled_notional"] = 0.0
    result = api.summarize_tca(
        frame, group_cols=["liquidity"], min_observations=1, min_coverage=0.5
    )
    assert sum(row["observation_count"] for row in result["groups"]) == 2
    missing = next(row for row in result["groups"] if row["group"]["liquidity"] is None)
    assert missing["coverage_ratio"] == 0.0
    assert missing["status"] != "ready"
    assert missing["recommended_shortfall_bps"] is None


def test_single_date_and_small_samples_have_no_ready_recommendation():
    api = _api()
    frame = _observations()
    frame["trade_date"] = "2024-01-02"
    row = api.summarize_tca(frame, group_cols=[], min_observations=3, min_coverage=0.0)["groups"][0]
    assert row["mean_ci_bps"] is None
    assert row["status"] != "ready"
    assert row["recommended_shortfall_bps"] is None
    assert "insufficient_dates" in row["reasons"]


@pytest.mark.parametrize("change", ["duplicate", "nonfinite", "overfill", "wrong_total", "date"])
def test_invalid_evidence_rejected(change):
    api = _api()
    frame = _observations()
    if change == "duplicate":
        frame["order_id"] = "a"
    elif change == "nonfinite":
        frame.loc[0, "total_bps"] = float("nan")
    elif change == "overfill":
        frame.loc[0, "filled_notional"] = 101
    elif change == "wrong_total":
        frame.loc[0, "total_cash"] = 5.0
    else:
        frame.loc[0, "trade_date"] = "invalid"
    with pytest.raises(ValueError):
        api.summarize_tca(frame, group_cols=[], min_observations=1, min_coverage=0.0)


def test_date_block_bootstrap_keeps_same_date_orders_together():
    api = _api()
    frame = _observations()
    repeated = pd.concat([frame, frame.assign(order_id=["c", "d"])], ignore_index=True)
    kwargs = {
        "group_cols": [],
        "min_observations": 2,
        "min_coverage": 0.0,
        "bootstrap_samples": 500,
        "seed": 7,
    }
    assert (
        api.summarize_tca(repeated, **kwargs)["groups"][0]["mean_ci_bps"]
        == (api.summarize_tca(frame, **kwargs)["groups"][0]["mean_ci_bps"])
    )


def test_zero_execution_across_dates_never_recommends_cost_evidence():
    frame = _observations()
    frame["filled_notional"] = 0.0
    frame["execution_cash"] = 0.0
    frame["opportunity_cash"] = frame["total_cash"]
    row = _api().summarize_tca(frame, group_cols=[], min_observations=2, min_coverage=0.0)[
        "groups"
    ][0]
    assert row["mean_shortfall_bps"] == pytest.approx(12.5)
    assert row["status"] == "insufficient_evidence"
    assert "no_execution_evidence" in row["reasons"]
    assert row["recommended_shortfall_bps"] is None
