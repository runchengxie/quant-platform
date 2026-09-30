# Run your first backtest

Language: English · [简体中文](first-backtest.zh-CN.md)

This guide uses a small synthetic dataset to demonstrate the full flow from scores and an execution model to backtest results. Prices and signals are for learning the API only; they do not express investment views.

## 1. Prepare data

The backtest input is a `pandas.DataFrame`. The smallest example uses these columns:

| Column | Meaning |
| --- | --- |
| `trade_date` | Trading date |
| `symbol` | Security identifier |
| `signal` | Score used to rank and select securities |
| `close` | Price used by the execution model |

The four synthetic securities below span three trading days and are ranked again each day:

```python
import pandas as pd

scores = pd.DataFrame(
    {
        "trade_date": pd.to_datetime(["2020-01-01"] * 4 + ["2020-01-02"] * 4 + ["2020-01-03"] * 4),
        "symbol": ["A", "B", "C", "D"] * 3,
        "signal": [4.0, 3.0, 2.0, 1.0, 3.0, 4.0, 2.0, 1.0, 3.0, 4.0, 2.0, 1.0],
        "close": [100.0, 100.0, 100.0, 100.0, 110.0, 90.0, 105.0, 100.0, 121.0, 81.0, 110.25, 100.0],
    }
)
```

## 2. Configure the execution model

The execution model defines entry and exit prices, costs, and slippage. Explicit transaction costs are set to zero here to keep the example easy to follow:

```python
from portfolio_backtester.execution import build_execution_model

execution = build_execution_model(
    {"entry": {"price_col": "close"}, "exit": {"price_col": "close"}},
    default_cost_bps=0.0,
    default_exit_price_policy="strict",
    default_exit_fallback_policy="ffill",
    default_price_col="close",
)
```

## 3. Configure the strategy and backtest

`StrategySpec` describes security selection and target weighting. `BacktestSpec` combines the strategy, execution model, and backtest schedule:

```python
from portfolio_backtester import BacktestSpec, StrategySpec, run_backtest

spec = BacktestSpec(
    strategy=StrategySpec(
        name="topk-demo",
        type="topk_buffered_long_only",
        score_col="signal",
        top_k=2,
        weighting="equal",
    ),
    execution=execution,
    rebalance_dates=tuple(pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])),
    shift_days=0,
    trading_days_per_year=252,
)

result = run_backtest(scores, spec)
if result is None:
    raise RuntimeError("No replayable positions were formed")
```

## 4. Read the results

The default return value contains five parts:

```python
stats, net_returns, gross_returns, turnover, periods = result

print(stats["total_return"])
print(net_returns)
print(periods[0]["entry_date"], periods[0]["exit_date"])
```

- `stats` is a summary-statistics dictionary.
- `net_returns` contains holding-period returns after modeled costs.
- `gross_returns` contains holding-period returns before modeled costs.
- `turnover` contains turnover for each holding period.
- `periods` stores dates, positions, and return details for each holding period.

See [understanding backtest results](understanding-results.md) for field details. For costs, slippage, or tradability constraints, continue to [costs and execution assumptions](../concepts/execution-costs.md).

## What this example leaves out

Real research also needs to:

- Use published data assets with version information.
- Make signal formation and availability times explicit.
- Check price, liquidity, and trading-status fields.
- Set costs, slippage, and market rules.
- Save configuration, positions, pricing data, and run artifacts.

This page explains the call flow only. Before formal research, read the [composable backtest specification](../concepts/backtest-spec.md) and [interpreting backtest results](../concepts/backtest-interpretation.md).
