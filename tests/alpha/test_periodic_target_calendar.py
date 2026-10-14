"""Synthetic exact-period target matching across calendar boundaries."""

import pandas as pd
import pytest
from alpha_research.fundamental_state import FundamentalTargetSpec
from alpha_research.periodic_fundamental_state import build_periodic_fundamental_target_panel


@pytest.mark.parametrize("horizon", [1, 2])
def test_periodic_targets_match_every_calendar_quarter(horizon):
    periods = pd.date_range("2023-03-31", periods=8, freq="QE")
    frame = pd.DataFrame(
        {
            "symbol": "SYNTHETIC",
            "report_period": periods,
            "available_date": periods + pd.Timedelta(days=40),
            "state": range(8),
        }
    )
    result = build_periodic_fundamental_target_panel(
        frame,
        (FundamentalTargetSpec("future_state", "state", "level"),),
        horizon_periods=horizon,
    )
    matched = result.frame.iloc[: 8 - horizon]
    assert matched["target_report_period"].tolist() == periods[horizon:].tolist()
    assert matched["future_state"].tolist() == list(range(horizon, 8))
    assert (
        matched["fundamental_label_end_date"].tolist()
        == (periods[horizon:] + pd.Timedelta(days=40)).tolist()
    )
    assert set(matched["report_period"].dt.quarter) == {1, 2, 3, 4}
    assert result.audit["complete_label_rows"] == 8 - horizon
    assert result.frame.iloc[8 - horizon :]["future_state"].isna().all()


@pytest.mark.parametrize(
    "start, end, months",
    [
        ("2024-02-29", "2024-03-31", 1),
        ("2023-02-28", "2023-03-31", 1),
        ("2024-04-30", "2024-05-31", 1),
        ("2024-02-29", "2025-02-28", 12),
        ("2024-02-29", "2024-08-31", 6),
        ("2024-09-29", "2024-12-29", 3),
        ("2024-01-30", "2024-02-29", 1),
    ],
)
def test_periodic_targets_preserve_month_end_and_ordinary_dates(start, end, months):
    periods = pd.to_datetime([start, end])
    frame = pd.DataFrame(
        {
            "symbol": ["SYNTHETIC"] * 2,
            "report_period": periods,
            "available_date": periods + pd.Timedelta(days=10),
            "state": [1.0, 2.0],
        }
    )
    result = build_periodic_fundamental_target_panel(
        frame,
        (FundamentalTargetSpec("future_state", "state", "level"),),
        horizon_periods=1,
        period_months=months,
    )
    row = result.frame.iloc[0]
    assert row["target_report_period"] == pd.Timestamp(end)
    assert row["future_state"] == 2.0
