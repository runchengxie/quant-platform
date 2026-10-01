# Backtest specification

Language: English · [简体中文](backtest-spec.zh-CN.md)

`BacktestSpec` is the recommended configuration entry point for score-driven portfolio backtests. It combines the existing `StrategySpec` and `ExecutionModel` types into one immutable configuration, replacing settings previously passed as separate `backtest_topk` arguments.

## Responsibilities

| Type | Responsibility |
| --- | --- |
| `StrategySpec` | Score column, Top-K size, long/short mode, weighting, holding buffers, and group caps |
| `ExecutionModel` | Entry prices, exit rules, costs, slippage, trading calendar, and price or liquidity constraints |
| `BacktestSpec` | Strategy and execution configuration, rebalance dates, holding period, annualization, and other run settings |

`BacktestSpec` does not introduce new selector, allocator, cost-model, or exit-rule types. Existing types continue to define strategy selection and execution semantics.

## Basic example

The example omits construction of the `scores` DataFrame. Inputs need at least `trade_date`, `symbol`, a score column, and the price columns used by the execution model.

```python
import pandas as pd

from portfolio_backtester import BacktestSpec, StrategySpec, run_backtest
from portfolio_backtester.execution import build_execution_model

execution = build_execution_model(
    {
        "cost": {"name": "bps", "bps": 10},
        "entry": {"price_col": "close"},
        "exit": {
            "price": "strict",
            "fallback": "ffill",
            "price_col": "close",
        },
    },
    default_cost_bps=0,
    default_exit_price_policy="strict",
    default_exit_fallback_policy="ffill",
)

spec = BacktestSpec(
    strategy=StrategySpec(
        name="topk-demo",
        type="topk_buffered_long_only",
        score_col="signal",
        top_k=20,
        buffer_exit=5,
        weighting="equal",
    ),
    execution=execution,
    rebalance_dates=(
        pd.Timestamp("2026-01-05"),
        pd.Timestamp("2026-01-12"),
    ),
    shift_days=1,
    trading_days_per_year=252,
)

result = run_backtest(scores, spec)
```

`run_backtest` returns the same result shape as `backtest_topk`. It returns `None` when no holding period can be calculated. Otherwise, it returns a statistics mapping, net- and gross-return series, a turnover series, and holding-period details.

## Score and new-name controls

Two research controls are disabled by default:

- `selection_min_score` is a hard score threshold. Long or descending selections retain securities with scores at or above the threshold; short or ascending selections retain scores at or below it. Missing or non-numeric scores are ineligible. The threshold applies before holding-buffer and score-margin retention, so existing holdings cannot bypass it.
- `max_new_names_per_rebalance` limits how many securities can be added relative to the previous non-empty portfolio in one rebalance. The first non-empty portfolio is not limited; an initial build after empty screening periods is still treated as initial construction. Long and short sides are counted separately.

When both fields are `None`, the original Top-K behavior is preserved. When enabled, the selector does not fill `top_k` with weaker names if too few securities pass the threshold or new-name limit. Price, liquidity, and tradability constraints run before new-name counting, so rejected securities do not consume the allowance. Group caps still apply to final holdings.

With either control enabled, a side with no eligible securities is represented as cash in Top-K return replay: gross return is zero, moving existing holdings to cash still incurs sell turnover and costs, and the period remains in the return series. The holdings-detail interface represents cash with no rows for that side in the period. Empty screening periods before the first eligible portfolio do not consume the initial-construction allowance.

`selection_min_score` takes precedence over the target-weight turnover limit. With `max_turnover_per_rebalance`, interpolated target weights are filtered again to remove existing holdings below the threshold, so enforcing the hard threshold can cause realized weight turnover to exceed the configured limit.

```python
conservative_spec = BacktestSpec(
    strategy=spec.strategy,
    execution=spec.execution,
    rebalance_dates=spec.rebalance_dates,
    shift_days=spec.shift_days,
    trading_days_per_year=spec.trading_days_per_year,
    selection_min_score=0.25,
    max_new_names_per_rebalance=2,
)
```

## Entry cutoff, fixed slots, and target-first selection

Three additional fields support a research baseline that does not backfill rejected candidates and can explicitly retain cash:

- `entry_rank_cutoff` is a strict rank limit for new securities. At `8`, a new security must rank in the top eight to enter. A holding buffer can retain existing holdings beyond that entry limit, but lower-ranked new candidates do not backfill the portfolio.
- `target_weight_policy="fixed_slot"` supports long-only equal-weight portfolios. Each target slot has weight `1 / top_k`; unfilled slots remain cash. For example, if a Top-10 selection contains eight securities, each receives weight `0.10` and total target exposure is `0.80`.
- `selection_price_policy="target_first"` freezes the target list from signals before checking entry-date price, liquidity, and tradability. A target that fails an entry constraint is not replaced by a lower-ranked security; its weight remains cash in the modeled portfolio.

The defaults are `None`, `"execution_aware"`, and `"normalized"`, respectively, so existing configurations and calls retain their behavior. `fixed_slot` with a non-equal-weight or long-short strategy raises an error. A low-turnover Top-10 baseline can combine `buffer_exit=5`, `buffer_entry=2`, `entry_rank_cutoff=8`, `target_weight_policy="fixed_slot"`, and `selection_price_policy="target_first"`; the thresholds still require separate empirical validation.

## Configuration serialization

`BacktestSpec` is a frozen dataclass. `to_mapping()` converts rebalance dates and built-in execution components to JSON- or YAML-compatible values:

```python
import json

payload = spec.to_mapping()
encoded = json.dumps(payload, ensure_ascii=False)
restored = BacktestSpec.from_mapping(json.loads(encoded))

assert restored == spec
```

The mapping contains `schema_version`, currently `1`. Reading an unknown version raises an error rather than silently applying potentially incorrect semantics.

Signal and market-data frames are not part of the configuration mapping. When signals and prices are in the same frame, call:

```python
run_backtest(scores, spec)
```

If the filtered signal frame lacks complete exit prices, pass a separate read-only pricing frame:

```python
run_backtest(filtered_scores, spec, pricing_data=published_prices)
```

## Compatibility with the legacy entry point

`backtest_topk` retains its existing arguments, defaults, return structure, and exception behavior. The compatibility entry point maps legacy settings as follows:

| Legacy arguments | New configuration |
| --- | --- |
| `pred_col`, `top_k`, `weighting`, `long_only` | `StrategySpec` |
| `buffer_exit`, `buffer_entry` | `StrategySpec` |
| `group_col`, `max_names_per_group` | `StrategySpec.group_cap` |
| `price_col`, `cost_bps`, exit rules | Default `ExecutionModel` |
| Explicit `execution` | `BacktestSpec.execution` |
| Rebalance dates, holding period, liquidity, ranking, score thresholds, new-name limits, and fixed-slot controls | `BacktestSpec` |

An explicitly supplied `execution` continues to override `price_col`, `cost_bps`, and legacy exit arguments. The compatibility entry point does not currently emit a deprecation warning; migration timing will be considered after downstream callers have been audited.

## Scope

`BacktestSpec` describes score-driven Top-K portfolio backtests. Deterministic replay from target positions remains in `PositionBacktestConfig` and `run_position_backtest`. The configuration does not handle data downloads, model training, task orchestration, or live execution.
