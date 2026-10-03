# Market benchmark comparisons

[中文页面](benchmark-ladder.md)

The platform supports two related comparisons. A benchmark configured for a backtest is part of that run's output. A benchmark ladder compares existing strategy returns with one or more benchmark-return files after the run.

## Benchmark for a backtest

Set exactly one of `backtest.benchmark_symbol` and `backtest.benchmark_returns_file`. When benchmark returns are available, the run can include `backtest.benchmark` and `backtest.active` in `summary.json`, plus `backtest_benchmark.csv` and `backtest_active.csv`.

For additional same-run comparisons, configure `backtest.benchmark_compare`. Each entry must provide exactly one of `symbol` or `returns_file`. The run writes `backtest_benchmark_compare_summary.csv` and a `backtest_benchmark_compare_<name>.csv` report for each entry. This adds comparisons without changing the primary benchmark.

## Post-run benchmark ladder

The `portfolio_backtester.benchmark_ladder` module compares existing strategy and benchmark returns. Its Python entry point is `build_benchmark_ladder(config, config_dir=...)`. No `strategy backtest benchmark-ladder` command is registered.

The configuration accepts a required `strategy_returns_file`, an optional `strategy_return_col`, `expected_market`, `periods_per_year`, and either a `primary_benchmark` object or a list of `comparisons`. Each benchmark entry can provide `name`, `market`, a returns-file path, an optional return-column name, and an optional attribution-file path. Relative paths are resolved from `config_dir`.

The CSV date column may be `trade_date`, `date`, `period_end`, or `index`. Unless a return column is specified, the module checks `strategy_return`, `benchmark_return`, `net_return`, `return`, and `active_return`. If an entry marks its source as daily, the module compounds daily returns over `periods_file` intervals; that file must contain `entry_date` and `exit_date`.

Each result row reports aligned periods, strategy and benchmark total returns, active return statistics, market labels, status, and any error. A mismatched market or no overlapping dates is reported as `incompatible`; missing benchmark input or unusable returns are reported as `unavailable`. `attribution_available` only reports whether the configured attribution file exists. The ladder does not calculate attribution.

The module defaults `periods_per_year` to `12`. Set it to match the return frequency when interpreting annualized statistics. The ladder is a comparison utility; it does not select a benchmark or establish that a strategy is investable.
