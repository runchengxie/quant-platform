from __future__ import annotations

import pandas as pd

from strategy_pipeline.pipeline.output_summary_sections import (
    _build_backtest_exposure_summary,
    _date_bounds_text,
    _frame_records,
)


def test_summary_helpers_normalize_paths_dates_and_frames() -> None:
    summary = _build_backtest_exposure_summary(
        style_path="artifacts/style.parquet",
        industry_path=None,
        active_summary_path="artifacts/active.json",
        style_summary={"latest_rebalance_date": "2026-01-02", "factors": {"size": 1}},
        industry_summary={"latest_entry_date": "2026-01-03"},
    )

    assert summary["style_file"] == "artifacts/style.parquet"
    assert summary["industry_file"] is None
    assert summary["latest_rebalance_date"] == "2026-01-02"
    assert summary["latest_entry_date"] == "2026-01-03"
    assert _date_bounds_text(["2026-01-03", "2026-01-01"]) == {
        "start": "20260101",
        "end": "20260103",
    }
    assert _frame_records(pd.DataFrame({"value": [1.0, None]})) == [
        {"value": 1.0},
        {"value": None},
    ]
