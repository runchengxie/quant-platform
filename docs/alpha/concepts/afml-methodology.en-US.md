# AFML research components

Language: English · [简体中文](afml-methodology.md)

This page documents financial machine-learning components implemented in `alpha_research`. They use owner-native APIs and do not import orchestration, portfolio-backtesting, or execution-layer implementations.

## Components

| Module | Purpose | Main output |
| --- | --- | --- |
| `alpha_research.event_labeling` | Volatility targets, triple-barrier labels, and meta-labels | `label_events.parquet` |
| `alpha_research.sample_weighting` | Label concurrency, average uniqueness, return attribution, time decay, and sequential bootstrap | `sample_weights.parquet`, `sample_weights.receipt.json` |
| `alpha_research.probability_calibration` | Isotonic and Platt calibration using historical windows, plus probability-to-bet-size mapping | Out-of-sample calibration report |
| `alpha_research.fracdiff` | Fixed-width fractional differentiation and selection of `d` within the training window | Feature evidence |
| `alpha_research.structural_breaks` | CUSUM, recursive-residual CUSUM, and SADF | Regime or break evidence |

## Event-table contract

`label_triple_barrier` returns an event table containing at least:

- `event_id`
- `symbol`
- `signal_date`
- `label_start`
- `label_end`
- `first_touch`
- `barrier`
- `target`
- `side`
- `realized_return`
- `side_adjusted_return`
- `label`
- `meta_label`

Reuse the same event table for labels, purging, embargo, and sample weighting. Separate modules should not infer their own approximate label horizons.

## Sample weights

A recommended formal candidate configuration is:

```python
from alpha_research.sample_weighting import SampleWeightConfig, build_event_sample_weights

weights, receipt = build_event_sample_weights(
    label_events,
    bar_index=trade_calendar,
    config=SampleWeightConfig(
        mode="uniqueness_time_decay",
        uniqueness_power=1.0,
        time_decay_halflife=252,
        min_weight=0.05,
    ),
)
```

Weights are normalized to mean 1. The receipt records the event hash, effective sample size, weight concentration, and average uniqueness.

A formal research protocol should reject promotion when event-window construction is incomplete. Exploratory runs may use a fallback, but must record it and report coverage.

## Probability calibration and meta-labels

Calibration may use only realized outcomes strictly earlier than the current scoring date. `expanding_probability_calibration` excludes same-day outcomes. Calibrated probabilities can be mapped to bet sizes, while final portfolio constraints, risk targets, and turnover limits remain owned by `portfolio-backtester`.

## Fractional differentiation

Select `d` within the training window or freeze it during a separate development period. Do not scan the full sample and choose `d` from final backtest performance. Report these measures for each candidate:

- ADF t-statistic
- Correlation with the original series
- Number of valid observations
- Feature-family ablation

## Structural breaks

CUSUM and SADF outputs are research features or diagnostic evidence. They must not directly trigger live orders or automatic model replacement. Aggregate higher-frequency inputs in the data layer first. `sadf_series` is intended for daily or pre-aggregated series, not raw tick-level order-book messages.
