# Out-of-sample bridge for incumbent requalification

Language: English · [简体中文](incumbent-requalification-oos-controls.md)

`portfolio_backtester.incumbent_requalification_oos` provides two daily out-of-sample bridges with the same portfolio policy and diagnostics:

- `stateful_incumbent_requalification_daily_rows` passes the previous day's target holdings into selection, allowing eligible incumbents to remain in the exit buffer.
- `stateless_incumbent_requalification_daily_rows` resets selection state each day, while still calculating target-weight changes and turnover across dates.

The selection stage is the only difference. Comparing `stateful - stateless` isolates the effect of the holding buffer. A production baseline should be evaluated separately against the complete candidate strategy.

When cash is allowed and no position qualifies on a date, the bridge gets the signal date and execution date from that day's candidate cross-section. It emits an empty portfolio, `cash_weight=1.0`, and zero cash return. If holdings existed on the prior date, the transition to cash still records sell weights, transaction costs, and blocked-fill diagnostics; it is not treated as a missing date.

## Fail-closed inputs

The scored input must explicitly contain:

- `hard_eligible`: full-universe hard eligibility for the date.
- `entry_eligible`: strict eligibility for new positions.

Missing either field raises an error. The bridge does not silently substitute `hard_eligible` for `entry_eligible`, which could turn a strict-candidate experiment into a full-market entry test.

`IncumbentRequalificationPolicy.rank_universe` determines the ranking scope. `hard_eligible` uses the compatibility full-market scope. `entry_plus_incumbents` ranks the union of new-entry candidates and daily rescored incumbents, while retaining the full input for hard-eligibility validation.

## Column mappings and execution prices

`IncumbentRequalificationConfig` can map date, symbol, score, industry, and eligibility columns. Before shared execution diagnostics run, the bridge normalizes mapped date and symbol columns to `trade_date` and `symbol`, keeping selection and replay mappings consistent.

The execution-price frame uses the standard portfolio-replay columns:

```text
trade_date
symbol
open
up_limit
down_limit
is_suspended
```

## Research boundary

The stateless path is a diagnostic control, not a production strategy. It tests whether incumbent buffering changes turnover or returns. Comparisons should also retain the frozen production baseline and use the same scores, candidate membership, cost model, and complete date set.
