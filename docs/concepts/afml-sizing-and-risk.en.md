# Portfolio Sizing and Strategy-Risk Evidence

Language: English · [简体中文](afml-sizing-and-risk.md)

This page describes the portfolio-layer sizing, active-bet aggregation, hierarchical risk parity (HRP), and strategy-risk utilities currently implemented in `portfolio_backtester`.

## Position sizing

`portfolio_backtester.bet_sizing` builds nonnegative, gross-normalized target weights from research inputs. Supported methods are `probability`, `probability_vol_target`, `signal_vol_target`, `confidence_budget`, and `risk_budget`. Optional controls include a gross target, per-name cap, discrete weight step, and minimum trade weight.

```python
from portfolio_backtester import SizingConfig, build_sized_weights

weights = build_sized_weights(
    candidates,
    score_col="signal_backtest",
    config=SizingConfig(
        method="probability_vol_target",
        single_name_cap=0.05,
        step_size=0.005,
        min_trade_weight=0.005,
    ),
)
```

The caller supplies `calibrated_probability` and, for volatility-targeted methods, `predicted_volatility` unless it overrides those column names. This helper does not train or calibrate a model. Probability calibration and its out-of-sample evidence belong to the research layer. Sizing constraints do not establish that inputs are predictive or that the resulting portfolio is suitable for live trading.

## Active bets

`average_active_bets` averages `bet_size` across events whose `label_start` and `label_end` include each timestamp. `discretize_weights` rounds weights to a supplied step. These are separate transformations; discretization alone does not enforce portfolio limits or turnover constraints.

## Hierarchical risk parity

`hierarchical_risk_parity` estimates HRP weights from a return DataFrame. `rolling_hrp_weights` estimates each rebalance using observations strictly earlier than that date and limits history to the configured lookback. HRP requires SciPy and at least two usable return series; missing covariance values are rejected.

These functions can be used for asset, model, or sleeve return series. They do not determine which series should be combined. Applying HRP to a changing daily Top-K stock universe is not automatically stable: inspect cluster and weight stability, turnover, and out-of-sample behavior before relying on it.

## Strategy-risk summaries

`portfolio_backtester.strategy_risk` provides probabilistic Sharpe ratio, positive/negative return concentration, hit ratio and average hit/miss, implied precision, strategy-failure probability, and implementation-shortfall/cost-resilience metrics. The exact fields are defined by the returned `StrategyRiskReport` and metric dictionaries.

`strategy_failure_probability` uses the observed payoff distribution and bets-per-year assumption to estimate the bootstrap probability that future precision falls below the precision implied by a target Sharpe. It is a research diagnostic, not account-level or portfolio Value-at-Risk.

## Run evidence

`portfolio_backtester.afml_evidence.generate_run_afml_evidence` reads a persisted run directory and writes sizing and strategy-risk evidence. It can also write HRP evidence when a returns input is configured. The generated files include:

```text
sizing_receipt.json
strategy_risk_report.json
hrp_receipt.json
hrp_weights.csv
```

HRP files are conditional on providing the HRP returns input. The orchestration layer can add evidence paths and hashes to a lineage sidecar. These reports are not order instructions: execution still consumes the standard `targets.json` contract.
