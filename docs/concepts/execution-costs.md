# Execution costs and assumptions

Language: English · [简体中文](execution-costs.zh-CN.md)

This page describes the cost and slippage models, price columns, liquidity constraints, and exit-price policies currently supported by the repository. The contracts are implemented in [`_execution_models.py`](https://github.com/runchengxie/quant-platform/blob/main/packages/portfolio-backtester/src/portfolio_backtester/_execution_models.py) and [`_execution_build.py`](https://github.com/runchengxie/quant-platform/blob/main/packages/portfolio-backtester/src/portfolio_backtester/_execution_build.py), with behavior covered by [`test_execution.py`](https://github.com/runchengxie/quant-platform/blob/main/tests/test_execution.py) and [`test_backtest.py`](https://github.com/runchengxie/quant-platform/blob/main/tests/test_backtest.py).

These features are intended for research backtests. Recalibrate parameters for the market, account, broker, and execution method being studied. Defaults are starting points, not current broker quotes.

## Execution model components

`ExecutionModel` contains five components:

| Component | Responsibility |
| --- | --- |
| `entry_policy` | Selects the entry price column |
| `exit_policy` | Selects the exit price column and handling for missing prices |
| `cost_model` | Estimates commissions, taxes, and other explicit costs |
| `slippage_model` | Estimates spread and market impact |
| `selection_constraints` | Filters candidates by price and liquidity |

The model can also specify a trading calendar and additional open or closed dates.

## Cost models

### Fixed basis-point cost

`BpsCostModel` calculates cost from turnover and a basis-point rate.

Initial construction charges one-way cost on gross portfolio exposure. Later rebalances default to round-trip cost; set `round_trip=False` for one-way cost.

### Side-specific basis-point cost

`SideBpsCostModel` accepts separate rates for:

- Long entries
- Long exits
- Short entries
- Short exits
- Daily short-borrow cost

Use this model when trading direction has different assumed rates.

### Detailed A-share trade-fee model

`DetailedTradeFeeModel` combines commission, stamp duty, transfer fees, minimum commission, and slippage.

Directly constructing `DetailedTradeFeeModel()` uses these defaults:

| Parameter | Default |
| --- | ---: |
| Buy commission | 2.5 bps |
| Sell commission | 2.5 bps |
| Sell stamp duty | 5.0 bps |
| Transfer fee | 0.1 bps |
| Minimum commission floor | CNY 5 |
| Buy slippage | 6.0 bps |
| Sell slippage | 8.0 bps |
| Portfolio value | CNY 1,000,000 |

The commission floor applies to the aggregate entry or exit notional passed to the model. Turnover weights are converted into notional using `portfolio_value`, so portfolio size affects the cost result.

When built from a configuration mapping, unspecified directional slippage defaults to 10 bps for both buys and sells. This differs from the 6 bps buy and 8 bps sell defaults of direct construction. Set `buy_slippage_bps` and `sell_slippage_bps` explicitly in formal research.

Slippage embedded in this fee model is included in `fee_cost`. Configuring a separate slippage model adds a second slippage assumption. To report fees and slippage separately, set the fee model's directional slippage to zero and use the separate model.

The default rates do not represent any broker's current fee schedule. Adjust them for the account and backtest period.

### Disabling explicit costs

`NoCostModel` returns zero explicit cost. The configuration names `none`, `off`, and `zero` construct this model.

## Slippage models

### Fixed basis-point slippage

`BpsSlippageModel` multiplies the absolute trade weight by a fixed basis-point rate.

### Participation-based slippage

`ParticipationSlippageModel` estimates trade participation using portfolio value, trade weights, and a liquidity column. Its approximate calculation is:

```text
Trade notional = abs(trade weight) × portfolio_value
Participation = trade notional ÷ amount_col
Per-security slippage (bps) = base_bps + impact_bps × participation ^ power
```

`max_participation` can cap the participation used in the estimate. This stabilizes the estimate; it does not schedule multi-day execution or reject oversized orders.

Set the liquidity column with `amount_col`. For open-price execution, prefer a lagged liquidity measure known before the open, such as `adv20_amount` calculated through the prior session. Using the current day's full traded value introduces look-ahead information.

### Price-tiered slippage helper

`l2_price_tiered_slippage` returns a research slippage rate based on closing-price tiers. The sell-side rate adds 2 bps to the buy-side baseline.

The helper uses a built-in price-tier table. It does not read a live order book or update rates by security, date, or order size. Treat it as a simplified assumption; it does not calculate live quotes.

## Entry and exit prices

`EntryPolicy` selects the column used for entry, such as `open`, `close`, or another column prepared by the caller.

`ExitPolicy` supports three exit rules:

| Rule | Behavior |
| --- | --- |
| `strict` | If the planned exit date has no valid price or the security is not tradable, no exit price is returned for that security |
| `ffill` | Find the most recent valid price on or before the planned exit date |
| `delay` | Find the first valid price on or after the planned exit date |

`delay` can use `fallback_policy='ffill'`. If no later valid price is found, the model falls back to the most recent valid price on or before the planned date. With `none`, it does not fall back.

Tradability is supplied through a caller-provided Boolean column. The model can only use the state in that column; it does not infer price limits, T+1 sellability, suspension causes, order rejections, or broker rules.

## Price columns and intraday data

`PositionBacktestConfig` can set these columns separately:

- `price_col`
- `entry_price_col`
- `exit_price_col`

When `entry_price_col` or `exit_price_col` is unset, it falls back to `price_col`.

`run_position_backtest` also accepts `intraday_bars`. When intraday data is supplied, the function calculates intraday volume-weighted prices and overrides corresponding daily entry and exit prices where available. Missing intraday values continue to use the daily price table.

## Meaning of `tr_close`

The package treats `tr_close` as an ordinary caller-supplied price column. The repository does not download adjustment factors or build a cash-dividend ledger.

Before using `tr_close`, confirm with the data provider:

- Whether the series is forward-adjusted, backward-adjusted, or total-return adjusted
- How dividends and stock splits are handled
- What fallback is used when adjustment factors are missing
- Whether the convention is consistent across securities and periods

`tr_close` can reduce price jumps caused by ex-dividend and split events. It does not represent the actual dividend payment date, after-tax cash, reinvestment timing, or account-level cash flows.

## Configuration example

This example combines side-specific fees, participation-based slippage, open-price entry, and delayed exit:

```python
from portfolio_backtester.execution import build_execution_model

execution = build_execution_model(
    {
        "cost": {
            "name": "side_bps",
            "buy_bps": 6,
            "sell_bps": 8,
        },
        "slippage": {
            "name": "participation",
            "base_bps": 2,
            "impact_bps": 10,
            "amount_col": "adv20_amount",
            "portfolio_value": 1_000_000,
            "power": 0.5,
        },
        "entry": {
            "price_col": "open",
        },
        "exit": {
            "price": "delay",
            "fallback": "ffill",
            "price_col": "close",
        },
        "constraints": {
            "min_price": 2,
            "min_amount": 5_000_000,
            "amount_col": "adv20_amount",
        },
    },
    default_cost_bps=0,
    default_exit_price_policy="strict",
    default_exit_fallback_policy="ffill",
)
```

The pricing data must provide `open`, `close`, and `adv20_amount`.

## Scope and limitations

The current implementation supports:

- Daily or lower-frequency portfolio research
- Comparing cost and slippage assumptions
- Sensitivity analysis for liquidity filters and delayed exits
- Replaying externally generated target positions

More detailed implementations are needed for:

- Tick- or order-book-level matching
- Real order queues and partial fills
- Account-level cash, taxes, and dividend ledgers
- T+1 sellable quantities
- Short availability and dynamic borrow fees
- Broker rejections and exchange microstructure rules

Backtest results depend heavily on input data and execution assumptions. Preserve the price columns, cost parameters, slippage parameters, portfolio value, and source of tradability flags with each report.
