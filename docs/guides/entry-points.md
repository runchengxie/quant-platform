# Common entry points

Language: English · [简体中文](entry-points.zh-CN.md)

`portfolio-backtester` provides five public ways to move from a backtest specification to position replay and benchmark evaluation. For a new score-driven backtest, start with `BacktestSpec` and `run_backtest`.

## 1. Run a backtest from a composable specification

Use `StrategySpec` for selection and weighting settings, `ExecutionModel` for entry and exit behavior, costs, slippage, and selection constraints, and `BacktestSpec` for the rebalance schedule and other run-level settings.

```python
import pandas as pd

from portfolio_backtester import BacktestSpec, StrategySpec, run_backtest
from portfolio_backtester.execution import build_execution_model

# Build scores with trade_date, symbol, signal, and close columns.
execution = build_execution_model(
    None,
    default_cost_bps=10.0,
    default_exit_price_policy="strict",
    default_exit_fallback_policy="ffill",
    default_price_col="close",
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

`BacktestSpec.to_mapping()` returns a JSON/YAML-safe configuration, and `BacktestSpec.from_mapping()` restores it. Market frames stay outside the mapping and are supplied to `run_backtest` at runtime.

For low-turnover selection, set `selection_min_score` and `max_new_names_per_rebalance`. To cap entry ranks and leave unfilled slots in cash, combine `entry_rank_cutoff` with `target_weight_policy="fixed_slot"`. Set `selection_price_policy="target_first"` when target names should be selected before entry-date price or tradability checks. The defaults preserve the existing behavior: no entry-rank cutoff, normalized target weights, and execution-aware selection. See [Composable backtest specification](../concepts/backtest-spec.md) for the complete field semantics.

The score frame generally needs these columns:

- `trade_date`
- `symbol`
- A score column such as `signal`
- A price column such as `close`
- Any liquidity or tradability columns required by the execution model

## 2. Use the historical Top-K compatibility API

`backtest_topk` retains the historical parameter-based interface. It converts those arguments into `StrategySpec`, `ExecutionModel`, and `BacktestSpec`, then calls the unified execution path.

```python
from portfolio_backtester import backtest_topk
```

## 3. Construct positions before running the backtest

Use `StrategySpec` with `construct_positions_from_strategy` to create standard target positions, then pass those positions to `run_position_backtest`. This separates selection from position replay and makes the target positions available for inspection or reuse.

```python
from portfolio_backtester import StrategySpec, construct_positions_from_strategy
```

## 4. Replay existing target positions

Use `PositionBacktestConfig` and `run_position_backtest` when positions come from another model, optimizer, or manual process. This lower-level path calculates strategy returns, costs, and risk summaries. It does not take benchmark data as an input.

## 5. Evaluate a position backtest against a benchmark

Use `evaluate_position_backtest` when you need tracking error, Information Ratio, alpha, beta, correlation, and active-return statistics. Daily benchmark returns are compounded over each position period's entry and exit dates before they are aligned with strategy-period returns.

```python
from portfolio_backtester import PositionBacktestConfig, evaluate_position_backtest

evaluation = evaluate_position_backtest(
    positions=positions,
    pricing=pricing,
    periods=periods,
    config=PositionBacktestConfig(transaction_cost_bps=10.0),
    benchmark_return_series=benchmark_daily_returns,
)

strategy_stats = evaluation.backtest.summary["stats"]
benchmark_stats = evaluation.benchmark_stats
active_stats = evaluation.active_stats
```

Pass benchmark prices with `benchmark_df` instead when returns should be derived from a price frame. If benchmark price columns differ from the strategy's columns, set `benchmark_entry_price_col` and `benchmark_exit_price_col` explicitly.
