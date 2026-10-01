# StyleReplica Alpha Signal Research

> Simplified Chinese reference: [StyleReplica Alpha 信号研究](style-replica.md).

`alpha_research.style_replica` maintains StyleReplica factors, research classifications, A/B scores, and standard signal artifacts. Final slot allocation, theme quotas, holding buffers, replacement limits, overlap handling, and portfolio weights have moved out of the alpha owner.

Pipeline orchestration and `targets.json` export belong to `strategy_pipeline`. The frozen StyleReplica policy belongs to `strategy-app`. Generic target holdings, backtesting, costs, and capacity belong to `portfolio_backtester`.

## Module entry points

```python
from alpha_research.style_replica import (
    StyleReplicaConfig,
    StyleReplicaSignalGenerator,
    generate_daily_signals,
    map_stock_to_theme,
)
```

The package no longer exposes `StyleReplicaPortfolioConfig`, `build_style_replica_positions`, holding-change builders, or portfolio exposure builders.

## Signal layer

`StyleReplicaSignalGenerator` accepts prices, turnover, market capitalization, industry, and security reference information. It computes two research scores, A and B.

Security eligibility used for backtests or simulations must be dated and include `symbol`, `trade_date`, `is_st`, `st_available_from`, `is_suspended`, and `list_date`. An ST state is known for a decision only when `st_available_from` is no later than that decision date. Missing availability or a date after the decision leaves eligibility unknown, so the security is excluded from the candidate universe. Legacy `daily_clean` assets without this field cannot provide the new point-in-time guarantee. The current security name cannot substitute for historical ST status. Without security eligibility input, exploratory scores can still be generated, but `eligible_for_backtest` and `eligible_for_live` are false. Historical prices only contribute factors available at the time. The latest date's universe must not be projected backward across the sample.

Score A mainly uses residual volatility, liquidity, market capitalization, 20-day and 120-day momentum, market beta, industry momentum, and optional minute-trading activity. Score B mainly uses volatility convergence, low residual volatility, liquidity, 20-day and 120-day momentum, and an optional Hermite stability measure.

Standard signal artifacts include:

| Field | Meaning |
| --- | --- |
| `signal_date` | Signal date |
| `symbol` | Security identifier |
| `score_a` | Research score A |
| `score_b` | Research score B |
| `raw_pred` | Unified research ranking score |
| `signal_eval` | Evaluation score |
| `signal_backtest` | Final score consumed by downstream portfolio backtests |
| `leg` | Candidate leg from research classification |
| `theme` | Research theme classification, without theme quotas |
| `industry` | Industry |
| `model_version` | Alpha model version |
| `feature_set_id` | Feature-set identifier |

The standard signal filename is `signals_style_replica.parquet`; metadata is stored in `signals_style_replica.meta.json`.

`signal_backtest` is a score. It does not represent portfolio returns, executions, or account NAV.

## Configuration boundary

`StyleReplicaConfig` contains alpha research parameters and model/feature identity only. Slot counts, theme quotas, industry limits, buffers, replacement rules, overlap settings, and final weights are outside this configuration.

Strategy parameters are frozen by `strategy_app.style_replica.StyleReplicaPolicy` and converted into the generic sleeve portfolio specification in `portfolio-backtester`.

```text
alpha_research.style_replica
    signals
      ↓
strategy_app.style_replica.StyleReplicaPolicy
      ↓
portfolio_backtester.sleeve_portfolio
    positions_by_rebalance
```

## Theme mapping

`theme_map` maps a security to a research theme. It retains theme keys, display labels, industry mappings, and concept-keyword mappings.

It does not define how many securities to buy in each theme. Theme quotas are strategy policy and belong to `strategy-app`.

## Signal stability

The alpha layer may measure changes in Top-K membership using `topk_membership_churn`. This metric measures changes in the research signal set.

It does not apply portfolio buffers, weights, industry limits, execution feasibility, or transaction costs. `portfolio-backtester` calculates formal portfolio turnover after target holdings are generated.

## Cross-layer boundaries

Develop new factors, scores, signal artifacts, IC, recency, and other research diagnostics here.

Manage slots, buffers, replacement, overlap, final weights, portfolio costs, and capacity in `portfolio-backtester`. Manage StyleReplica A/B identity, theme quotas, and frozen strategy versions in `strategy-app`.

Alpha research code must not import `portfolio_backtester` or `quant_execution_engine` at runtime.
