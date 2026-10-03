# Turnover definitions

[中文页面](turnover.md)

`portfolio-backtester` reports two different measures that are often both called turnover:

| Field | Meaning | Use |
| --- | --- | --- |
| `name_turnover` | Share of current holdings that were replaced | Describe Top-K membership stability |
| `TurnoverBreakdown.one_way_turnover` | One-way turnover derived from weight changes | Estimate transaction costs |

## `TurnoverBreakdown`

The breakdown keeps these values separate:

- `buy_weight`: total weight bought
- `sell_weight`: total weight sold
- `gross_traded_weight`: buys plus sells
- `half_l1_turnover`: one half of the absolute weight changes
- `one_way_turnover`: the backtester's cost-accounting convention

For a rebalance after the initial build:

```text
half_l1_turnover = 0.5 * sum(abs(target_weight - drifted_weight))
```

For the initial build, `one_way_turnover` equals the total amount bought. Later it equals `half_l1_turnover`. The `half_l1_turnover` field always keeps the mathematical half-L1 definition.

## `RebalanceTurnoverReport`

The report separates target changes, pre-trade demand, and observed execution:

- `target_entered_names`, `target_exited_names`, and `target_overlap_names` list the names entering, leaving, or remaining in the target holdings. The matching `*_count` fields give their counts.
- `target_name_turnover` measures target-name replacement and is retained for compatibility.
- `target_weight_full_l1` and `target_weight_half_l1` compare the requested target weights across periods, before current-period price drift.
- `pretrade_demand_buy`, `pretrade_demand_sell`, `pretrade_demand_full_l1`, and `pretrade_demand_half_l1` compare drifted holdings with the weights requested for the current rebalance.
- `executed_buy` and `executed_sell` report observed executed weights.
- `executed_full_l1` and `executed_half_l1` report observed execution turnover. `executed_gross` remains a compatibility alias for `executed_full_l1`.
- `executed_cost` is populated only when the caller supplies observed execution cost.
- `target_gross_exposure` and `target_cash_weight` describe the frozen target; `modeled_gross_exposure` and `modeled_cash_weight` describe modeled holdings after opening constraints.

Weights and turnover are fractions of portfolio NAV at the start of the period; `1.0` means 100% of that NAV. `executed_cost` is a return-drag fraction of starting NAV, not a currency amount.

A score backtest has no fill report. Its period-level `executed_buy`, `executed_sell`, `executed_gross`, `executed_full_l1`, `executed_half_l1`, and `executed_cost` values are therefore `None`, not zero. `modeled_fee_cost`, `modeled_slippage_cost`, and `modeled_total_cost` are estimates and must not be described as observed fills.

Summary fields named `avg_*` include the initial build. Their `avg_rebalance_*` counterparts exclude periods with `is_initial_build=true` and describe subsequent rebalances. The target and modeled exposure fields also have these average summaries.

For an equal-weight Top-10 portfolio that replaces two names, target-weight full-L1 is `0.40` and half-L1 is `0.20`. `max_positive_names` can reject a weight interpolation that produces too many positive-weight names.

## Session-based schedules

`SessionRebalanceSchedule` defines a rebalance interval in trading sessions. `rebalance_interval_sessions=3` means a full rebalance every three sessions, with holdings kept until the next scheduled rebalance. It does not start a new three-session sleeve every day.

## Annualization

`annualize_turnover` applies linear annualization to describe trading intensity. It does not represent compounded returns.
