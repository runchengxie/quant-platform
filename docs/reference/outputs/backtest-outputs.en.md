# Backtest output reference

Language: English · [简体中文](backtest-outputs.md)

This page documents report files and fields produced by portfolio-backtest workflows. For orchestration and the general artifact lifecycle, see [Output summaries](../../orchestration/output-summary.md). For `summary.json` and file handoff contracts, see the [Public API and artifact contract](../../reference/public-api.md).

## Construction-grid comparison

`strategy backtest construction-grid` prints JSON rows when no output path is configured. `--output` or `output_csv` writes CSV; `--output-json` or `output_json` writes JSON. The command reads a construction-grid YAML file, an existing run's `summary.json`, and `eval_scored.parquet`. It evaluates construction variants against the same scored data; it does not retrain the model.

CSV and JSON rows use the same fields:

```text
variant,scored_file,summary_path,target_col,price_col,eval_signal_col,backtest_signal_col,top_k,rank_offset,short_k,long_only,cost_bps,buffer_exit,buffer_entry,weighting,weighting_liquidity_col,liquidity_floor_col,liquidity_floor_quantile,max_turnover_per_rebalance,score_postprocess_method,score_postprocess_columns,dynamic_ensemble_active,dynamic_ensemble_signal_cols,dynamic_ensemble_avg_active_factor_count,dynamic_ensemble_avg_factor_turnover,dynamic_ensemble_avg_stock_turnover,factor_correlation_threshold,risk_penalty_columns,risk_penalty_strength,eval_ic_mean,eval_ic_ir,eval_long_short,eval_turnover_mean,backtest_periods,backtest_total_return,backtest_gross_total_return,backtest_ann_return,backtest_ann_vol,backtest_sharpe,backtest_max_drawdown,backtest_avg_turnover,backtest_avg_cost_drag,active_total_return,information_ratio,tracking_error,beta,alpha,corr,benchmark_name,benchmark_returns_file,exposure_available,status,error
```

- `status=ok` means the variant formed a portfolio and completed the backtest. `status=failed` means a required scored artifact, column, benchmark, or valid portfolio was unavailable; `error` records the reason.
- `backtest_total_return` is net of costs. `backtest_gross_total_return` uses the same holdings path before costs.
- `active_total_return`, `information_ratio`, `tracking_error`, `beta`, `alpha`, and `corr` are populated only when usable benchmark returns are configured.
- `exposure_available` indicates that the variant has an input signal for a later exposure or attribution check. It does not mean industry or style neutralization was run.

If `construction_grid.rolling_selection.output_json` is set, the command also writes a `portfolio_backtester.construction_grid_rolling_selection` JSON report. It ranks variants by `objective_col`, but changes from `previous_variant` only when the improvement exceeds `switch_penalty + min_improvement`; otherwise it retains the previous variant.

## Benchmark ladder

The `backtest.benchmark_compare` setting adds same-run benchmark comparisons and writes a summary CSV plus a report CSV for each comparison. For a post-run comparison of existing return files, use the `portfolio_backtester.benchmark_ladder` Python module. It has no registered `strategy backtest benchmark-ladder` CLI command. See the [benchmark comparison guide](../../concepts/benchmark-ladder.en-US.md).

## Positions

The fields in `positions_by_rebalance.csv`, `positions_current.csv`, and rebalance-diff files are documented in the [positions output contract](positions.md).

## Execution simulation and capacity

`execution_sim_*.csv` and `capacity_*.json` contain execution-simulation and capacity-stress outputs. See the [execution simulation guide](../../guides/execution-simulation.en.md) and [AFML sizing and risk](../../concepts/afml-sizing-and-risk.md).
