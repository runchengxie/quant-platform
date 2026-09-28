from __future__ import annotations

import pandas as pd
import pytest

from portfolio_backtester.point_in_time import PointInTimeDataView, PointInTimeTable


def _clock(cutoff: str) -> dict[str, object]:
    return {
        "schema_version": "research.clock.v1",
        "timezone": "Asia/Shanghai",
        "information_cutoff_at": cutoff,
        "signal_at": "2024-01-31T15:01:00+08:00",
        "decision_at": "2024-01-31T15:02:00+08:00",
        "earliest_order_at": "2024-02-01T09:30:00+08:00",
        "execution_window_start_at": "2024-02-01T09:30:00+08:00",
        "execution_window_end_at": "2024-02-01T15:00:00+08:00",
        "valuation_at": "2024-02-01T15:01:00+08:00",
        "timing_policy_id": "next-session",
        "trading_calendar_ref": "synthetic-calendar",
    }


def test_view_hides_future_event_and_late_publication() -> None:
    source = pd.DataFrame(
        {
            "symbol": ["A", "B", "C"],
            "event_at": [
                "2024-01-30T15:00:00+08:00",
                "2024-01-31T15:00:00+08:00",
                "2024-02-01T15:00:00+08:00",
            ],
            "available_at": [
                "2024-01-31T14:00:00+08:00",
                "2024-01-31T15:30:00+08:00",
                "2024-01-31T14:00:00+08:00",
            ],
        }
    )
    view = PointInTimeDataView({"bars": PointInTimeTable(source, "available_at", "event_at")})
    source.loc[0, "symbol"] = "MUTATED"
    result = view.at(_clock("2024-01-31T15:00:00+08:00")).read("bars")
    assert result.symbol.tolist() == ["A"]
    result.loc[0, "symbol"] = "OTHER"
    assert view.at(_clock("2024-01-31T15:00:00+08:00")).read("bars").symbol.tolist() == ["A"]


def test_view_rejects_unknown_or_naive_availability() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        PointInTimeTable(pd.DataFrame({"available_at": ["2024-01-31"]}), "available_at")
    with pytest.raises(ValueError, match="unknown timestamp"):
        PointInTimeTable(pd.DataFrame({"available_at": [None]}), "available_at")
