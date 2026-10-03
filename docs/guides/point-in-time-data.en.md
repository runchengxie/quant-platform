# Point-in-time research data

Language: English · [简体中文](point-in-time-data.md)

`portfolio_backtester.point_in_time.PointInTimeDataView` binds each strategy decision to a `research.clock.v1` clock. A read includes only rows whose publication time is no later than `information_cutoff_at`. For data with an event date, configure `event_at_col` as well. Both timestamp columns must contain timezone-aware values; missing or naive timestamps are rejected.

```python
from portfolio_backtester.point_in_time import PointInTimeDataView, PointInTimeTable

view = PointInTimeDataView(
    {
        "financials": PointInTimeTable(financials, available_at_col="published_at"),
        "daily_bars": PointInTimeTable(
            bars, available_at_col="available_at", event_at_col="session_close_at"
        ),
    }
)

for decision_clock in decision_clocks:
    data = view.at(decision_clock)
    visible_financials = data.read("financials")
    visible_bars = data.read("daily_bars")
    targets = strategy(visible_financials, visible_bars)
```

Supply the source's actual availability time. A trading date or reporting-period end is not a substitute for publication time. Bind a separate clock to every rebalance decision; one job-level clock does not represent a multi-year sequence of decisions.

This view filters only tables read through it. It cannot detect a strategy that reads the original full dataset through another path. Save input digests and each decision clock with generated targets. Execution simulation and result-bundle validation provide additional checks, but do not establish source availability on their own.
