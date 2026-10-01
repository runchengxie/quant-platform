# Cost breakdown

Language: English · [简体中文](cost-breakdown.zh-CN.md)

`CostBreakdown` provides a consistent view of portfolio-backtest costs. See the [`CostBreakdown` implementation](https://github.com/runchengxie/quant-platform/blob/main/packages/portfolio-backtester/src/portfolio_backtester/types.py) and its [tests](https://github.com/runchengxie/quant-platform/blob/main/tests/test_cost_breakdown.py).

| Field | Meaning |
| --- | --- |
| `fee_cost` | Aggregate fee components: commission, stamp tax, and transfer fees |
| `slippage_cost` | Aggregate spread, impact, opportunity, and financing components |
| `total_cost` | `fee_cost + slippage_cost` |

The current breakdown also exposes eight auditable sub-items:

| Aggregate | Sub-items |
| --- | --- |
| `fee_cost` | `commission`, `stamp_tax`, `transfer_fee` |
| `slippage_cost` | `spread_cost`, `temporary_impact`, `permanent_impact`, `opportunity_cost`, `financing_cost` |

When built with `CostBreakdown.from_components`, each aggregate equals the sum of its sub-items, and `total_cost` equals the sum of all eight. Existing callers can still pass only `fee_cost` and `slippage_cost`; sub-items then default to zero and are not a decomposition of those aggregates.

`DetailedTradeFeeModel` also includes directional slippage in its returned fee cost. Therefore, `fee_cost` does not always represent only commissions and taxes. Combining that model's embedded slippage with a separate slippage model adds both assumptions. To report them separately, set `buy_slippage_bps` and `sell_slippage_bps` to zero on `DetailedTradeFeeModel`, then calculate `slippage_cost` through the separate model.

Reports should preserve the cost model, slippage model, and all parameters. Do not infer an unreported sub-item from an aggregate total; retain only components actually supplied by the calculation.
