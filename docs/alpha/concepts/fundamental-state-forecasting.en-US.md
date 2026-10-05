# Fundamental-state forecasting

Language: English · [简体中文](fundamental-state-forecasting.md)

`alpha_research.fundamental_state` provides a research workflow that forecasts a future accounting measure, evaluates that forecast, and can combine it with current valuation in a cross-sectional score. Its target is a future financial statement value, not a stock return. This target definition is separate from the DailyWatch20 fundamental shadow.

The current implementation supports one-year annual targets. The input must contain one canonical, PIT-audited row per `(symbol, report_period)` and a valid `available_date`. The data platform owns revision selection and PIT provenance.

## Build targets and a persistence baseline

```python
from alpha_research.fundamental_state import (
    FundamentalTargetSpec,
    build_annual_fundamental_target_panel,
    build_persistence_baseline,
)

specs = (
    FundamentalTargetSpec("delta_roa_1y", "roa", "delta"),
    FundamentalTargetSpec("revenue_growth_1y", "revenue", "pct_change"),
    FundamentalTargetSpec("future_gross_margin_1y", "gross_margin", "level"),
)
targets = build_annual_fundamental_target_panel(annual_frame, specs)
baseline = build_persistence_baseline(targets.frame, specs[0])
```

The target panel records `feature_as_of_date`, `target_report_period`, `target_available_date`, and `fundamental_label_end_date`. Percentage change is defined only for a positive finite current value; otherwise it is missing. The persistence baseline predicts no change for `delta` and `pct_change` targets, and carries the current value forward for a `level` target.

Compare more complex models with this simple baseline. If they do not reliably improve out-of-sample results, added complexity is not justified by the model name alone.

## Leakage-safe walk-forward forecasts

`run_walk_forward_fundamental_forecast` creates expanding-window forecasts by formation period. Training labels must have become available before the earliest feature date in the test formation. It returns `pred_persistence` and configured model prediction columns, including `pred_ridge` or `pred_xgb` when those models are requested.

```python
from alpha_research.fundamental_state import run_walk_forward_fundamental_forecast

run = run_walk_forward_fundamental_forecast(
    targets.frame,
    target_spec=specs[0],
    feature_cols=("roa", "gross_margin", "revenue_growth_history"),
    model_configs={
        "ridge": {"type": "ridge", "params": {"alpha": 1.0}},
        "xgb": {"type": "xgb_regressor", "params": {}},
    },
    min_train_rows=500,
    min_train_periods=5,
)
```

The runner expects the caller to prepare missing values, winsorization, and cross-sectional scaling. It does not fit preprocessing silently. For a formation period whose companies have different report availability dates, it uses the earliest feature date as the training cutoff. This is conservative: it may exclude some recently disclosed labels to avoid using information unavailable to the earliest-trading sample.

## Evaluate forecasts and control overlapping labels

`evaluate_fundamental_forecast` reports count, MAE, RMSE, and rank IC, with optional directional accuracy. If a date column is supplied, rank IC is computed within each date cross-section and then averaged across valid dates. Without a date column, it uses the full-sample rank correlation. Do not mix years with different value scales into one cross-sectional IC.

Use `purge_and_embargo_fundamental_rows` when training-label windows can overlap the test interval. It removes labels that overlap the test dates and, when configured, observations that start during the following embargo period. In a strictly expanding walk-forward split, later observations are not added back to training, so embargo may have no effect; it matters more for CPCV and non-forward time splits.

## Combine forecasts with valuation

`build_fundamental_forecast_score` converts each selected input to a percentile within `signal_date`, then combines the percentiles using configured weights. For a lower-is-better measure, set `higher_is_better=False`.

Compare at least:

```text
current fundamentals only
forecast fundamentals only
current fundamentals + valuation
forecast fundamentals + valuation
```

This tests whether forecasts add information beyond current financial data. The score is a transparent cross-sectional ranking bridge, not a discounted-cash-flow valuation model. First test whether the financial state can be predicted; stock returns, Sharpe ratios, and portfolio costs are later questions. The implementation does not claim to reproduce the cited academic studies or their results.
