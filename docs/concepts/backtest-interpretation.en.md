# Interpreting backtest results

Language: English · [简体中文](backtest-interpretation.md)

This page explains portfolio backtest results. For prediction metrics such as IC, CPCV, PBO, and feature importance, use the result interpretation guide in `quant-market-research`. Run summaries and artifact lifecycle are described in [Output summary](../orchestration/output-summary.md); shared field contracts are in [Public API and artifact contracts](../reference/public-api.md).

## Net and gross returns

The main files are `backtest_net.csv` and `backtest_gross.csv`. Start with net returns: they include modeled trading costs and slippage. Gross returns show the same backtest before those costs. Neither series says whether the assumptions match live execution; check the run configuration and cost assumptions too.

## Main statistics

`summary.json` stores portfolio statistics under `backtest.stats`. Common fields include:

| Field | Meaning |
| --- | --- |
| `periods` | Number of return observations in the backtest. |
| `total_return` | Cumulative net return over the run. |
| `ann_return` | Annualized return using the configured period frequency. |
| `ann_vol` | Annualized standard deviation of period returns. |
| `sharpe` | Mean period return divided by period volatility, annualized with the configured frequency. |
| `max_drawdown` | Largest peak-to-trough decline in the compounded return series. |
| `avg_holding` | Mean holding-period length, usually in trading days. |
| `periods_per_year` | Annualization factor derived from holding-period and calendar settings. |
| `avg_turnover` | Mean turnover per rebalance period. |
| `avg_cost_drag` | Mean modeled cost per rebalance period. |

Return and cost fields are stored as decimal fractions: `0.01` means 1%. Turnover is also a fraction. Some reports display these values as percentages. Compare values only when the return period and conventions match.

## Drawdown and tail statistics

Additional fields include `sortino`, `calmar`, `drawdown_duration`, `recovery_time`, `drawdown_duration_days`, `recovery_time_days`, `skew`, `kurtosis`, `var_95`, and `cvar_95`.

- `sortino` uses downside deviation in place of total return volatility.
- `calmar` relates annualized return to the magnitude of maximum drawdown.
- `drawdown_duration` counts return periods from the prior peak to the trough; `drawdown_duration_days` records elapsed calendar days. `recovery_time` and `recovery_time_days` measure the trough-to-recovery interval.
- `skew` and `kurtosis` describe the shape and tails of the observed return distribution. They do not predict future extremes.
- `var_95` is the fifth percentile of period returns. `cvar_95` is the mean of observations at or below that threshold. These are historical sample statistics, not loss guarantees.

## Benchmark and active returns

When a benchmark is available, `summary.json` may include `backtest.benchmark` and `backtest.active`, alongside `backtest_benchmark.csv` and `backtest_active.csv`.

Common active fields are `tracking_error`, `information_ratio`, `beta`, `alpha`, `corr`, and `active_total_return`:

- `tracking_error` annualizes the standard deviation of strategy-minus-benchmark returns.
- `information_ratio` annualizes mean active return relative to active-return volatility.
- `beta` measures strategy-return covariance with benchmark returns relative to benchmark variance.
- `alpha` is an annualized estimate after the fitted beta adjustment.
- `corr` is the correlation of paired strategy and benchmark returns.
- `active_total_return` is the compounded strategy return relative to the compounded benchmark return.

These metrics use paired observations available for both series. Read the benchmark definition and coverage before comparing runs.

## Style and industry exposure

If the run has holdings and the input panel contains usable exposure columns, it may write `backtest_style_exposure.csv` and `backtest_industry_exposure.csv`. These describe portfolio exposures; they do not imply that the portfolio was neutralized. The `exposure-screen` protocol is a separate diagnostic for concentration against specified dimensions.

## Rolling Sharpe

`summary.json -> backtest.rolling_sharpe` records rolling Sharpe summaries and paths to their series files. Window settings appear in `windows_months`. Rolling values describe variation across historical windows; they are not independent observations or a stability guarantee. The rolling research implementation is in `alpha_research.recency_diagnostics`.

## Common reading errors

- Bucket IC, exposure analysis, and capacity stress tests answer different questions. Do not combine them into one conclusion.
- `hit_rate` is a supporting measure. It does not replace return, risk, cost, and benchmark analysis.
- A metric does not validate the data, point-in-time availability, or execution assumptions used to produce it. Check those inputs separately.
