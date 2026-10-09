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


def test_latest_visible_revision_is_order_independent_and_historical():
    frame = pd.DataFrame(
        {
            "symbol": ["A", "A", "B"],
            "revision": [1, 2, 1],
            "value": [10.0, 99.0, 5.0],
            "available_at": [
                "2024-01-02T12:00:00Z",
                "2024-01-04T12:00:00Z",
                "2024-01-02T12:00:00Z",
            ],
        }
    )
    for rows in [frame, frame.iloc[::-1]]:
        view = PointInTimeDataView({"fundamental": PointInTimeTable(rows, "available_at")})
        bound = view.at(_clock("2024-01-03T12:00:00Z"))
        assert hasattr(bound, "read_latest"), "latest visible revision API is missing"
        early = bound.read_latest("fundamental", identity_cols=["symbol"], revision_col="revision")
        assert early.set_index("symbol").value.to_dict() == {"A": 10.0, "B": 5.0}
        late = view.at(_clock("2024-01-05T12:00:00Z")).read_latest(
            "fundamental", identity_cols=["symbol"], revision_col="revision"
        )
        assert late.set_index("symbol").value.to_dict() == {"A": 99.0, "B": 5.0}
        assert len(view.at(_clock("2024-01-05T12:00:00Z")).read("fundamental")) == 3


@pytest.mark.parametrize("defect", ["ambiguous", "null_identity", "null_revision", "missing"])
def test_latest_revision_rejects_invalid_visible_keys(defect):
    frame = pd.DataFrame(
        {
            "symbol": ["A", "A"],
            "revision": [1, 2],
            "value": [10, 20],
            "available_at": ["2024-01-02T12:00:00Z"] * 2,
        }
    )
    if defect == "ambiguous":
        frame["revision"] = 1
    elif defect == "null_identity":
        frame.loc[0, "symbol"] = None
    elif defect == "null_revision":
        frame.loc[0, "revision"] = float("nan")
    else:
        frame = frame.drop(columns="revision")
    view = PointInTimeDataView({"data": PointInTimeTable(frame, "available_at")})
    bound = view.at(_clock("2024-01-03T12:00:00Z"))
    assert hasattr(bound, "read_latest"), "latest visible revision API is missing"
    with pytest.raises(ValueError):
        bound.read_latest("data", identity_cols=["symbol"], revision_col="revision")


def test_latest_revision_uses_ordered_revision_for_equal_availability():
    frame = pd.DataFrame(
        {
            "symbol": ["A", "A"],
            "revision": [2, 1],
            "value": [20, 10],
            "available_at": ["2024-01-02T12:00:00Z"] * 2,
        }
    )
    bound = PointInTimeDataView({"data": PointInTimeTable(frame, "available_at")}).at(
        _clock("2024-01-03T12:00:00Z")
    )
    assert hasattr(bound, "read_latest"), "latest visible revision API is missing"
    selected = bound.read_latest("data", identity_cols=["symbol"], revision_col="revision")
    assert selected.value.tolist() == [20]
