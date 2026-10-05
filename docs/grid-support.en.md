# Grid backtest helpers

Language: English · [简体中文](grid-support.md)

`portfolio_backtester.grid_support` provides reusable input, schedule, naming, and CSV helpers for backtest grids. It prepares evaluation inputs and result rows; it does not construct portfolios or make research decisions.

## Inputs and schedules

- `resolve_output_path` expands `~` and resolves relative output paths from the caller's current working directory.
- `parse_date_list` accepts compact `YYYYMMDD` and parseable date strings, removes blank or invalid values, then sorts and de-duplicates the dates.
- `resolve_rebalance_dates` uses explicit dates when supplied and keeps only dates present in the scored data. Otherwise it derives dates from the requested frequency and, when `min_symbols_per_date` is greater than one, filters dates that do not meet that symbol count.

## Stable run names and result rows

- `safe_run_name` builds a deterministic name from the base name, `top_k`, and cost in basis points. Buffer settings and weighting are included only when their corresponding flags are enabled; decimal points in cost are written as `p`.
- `GRID_RESULT_FIELDS` defines the fixed CSV column order. `init_grid_row` creates a strategy-neutral row with the run inputs and empty result fields.
- `write_grid_rows` creates the parent directory when needed and writes rows in the declared column order.

The helpers keep grid output structure stable across callers. Strategy-specific rules and interpretation remain with the caller.
