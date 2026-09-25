# LEAN differential feasibility spike

## Decision

Do not adopt LEAN as a `portfolio_backtester` differential backend in this
iteration. Keep it as an architecture reference. The proposed adapter would
need to recreate the platform's A-share execution rules and accounting around
LEAN's event-driven order engine, which would duplicate the native execution
simulator before parity or performance benefits have been established.

This is a no-adoption decision, not a parity result. The three replacement-gate
scenario requirements listed in the integration ledger were assessed against
the pinned LEAN source and its extension points. Only `liquid_long_only` has a
committed expected-result fixture in this repository. None of the scenarios
were submitted as LEAN backtests because doing so would require implementing
the very adapter and custom market models whose scope is the decision gate. No
production data or credentials were used.

## Pinned source and build

- LEAN: `QuantConnect/Lean` commit
  `f49bb9623a3e8782bf22bbd2cb51f691058cfdc3`.
- SDK: .NET `10.0.401`, installed under `/tmp/lean-spike` for this evaluation.
- Command: `dotnet build Launcher/QuantConnect.Lean.Launcher.csproj --configuration Release --nologo`.
- Result: build succeeded with 0 errors. It emitted 4,450 compiler and analyzer
  warnings. This proves that the pinned engine builds in the evaluation
  environment, not that it matches any platform scenario.
- Runtime parity, coverage ratio, and performance gates were not measured.

The source snapshot is available at
[QuantConnect/Lean commit f49bb962](https://github.com/QuantConnect/Lean/tree/f49bb9623a3e8782bf22bbd2cb51f691058cfdc3).
LEAN describes its models as pluggable. Relevant extension points include
[`IFillModel`](https://github.com/QuantConnect/Lean/blob/f49bb9623a3e8782bf22bbd2cb51f691058cfdc3/Common/Orders/Fills/IFillModel.cs),
[`IFeeModel`](https://github.com/QuantConnect/Lean/blob/f49bb9623a3e8782bf22bbd2cb51f691058cfdc3/Common/Orders/Fees/IFeeModel.cs),
[`ISettlementModel`](https://github.com/QuantConnect/Lean/blob/f49bb9623a3e8782bf22bbd2cb51f691058cfdc3/Common/Securities/ISettlementModel.cs),
exchange-hours data, and symbol properties. These interfaces make custom
behavior possible, but do not provide the required A-share semantics by
themselves.

## Replacement-gate scenario assessment

| Ledger scenario | LEAN source assessment | Adapter work implied | Decision |
|---|---|---|---|
| `liquid_long_only` | Generic equity orders, fills, fees, holdings, and portfolio value have corresponding LEAN primitives. The platform's period-based target and canonical frames still need translation. | Translate immutable positions/prices/periods, clock semantics, fees, and canonical result frames. Runtime parity was not run. | Possible in principle, insufficient to justify a second execution path alone. |
| `a_share_market_rules` | The pinned market-hours database and symbol-properties database contain no Shanghai or Shenzhen equity market entry. The only `China` symbol-properties match is a CME China futures contract. Generic lot-size support exists, but it does not define A-share odd-lot sells or T+1 sellable quantity. | Add A-share calendars, per-instrument rules, T+1 sellable inventory, price-limit and suspension fill checks, odd-lot liquidation, and the dated minimum-commission schedule. Connect them to order validation, settlement, fills, fees, and daily accounting. | Fails the no-duplication gate. |
| `capacity_partial_fill` | LEAN has order events and fill-model extension points. It does not directly implement the platform scenario's multi-day liquidity-capacity rule, cancel-replace policy, and unified cash/position conservation contract. | Reimplement native capacity scheduling and ledger translation, then reconcile each LEAN order event with canonical orders, fills, and daily ledger rows. | Fails the no-duplication gate. |

The platform's execution simulator currently spans 17 Python modules and 4,923
lines under `execution_sim/`, plus eight adjacent execution modules with 1,526
lines. These counts are a scope indicator, not an estimate that every line
would be ported. The required A-share and capacity behaviors cut across its
order generation, fill scheduling, market-rule checks, fees, cash, positions,
and daily NAV.

LEAN has configurable settlement, fill, and fee models, so this evaluation
does not claim the rules are impossible to model. The blocking issue is the
amount of duplicate market and ledger behavior needed to express and verify the
three ledger-defined scenarios. Because scenario parity and performance were not run,
the coverage ratio gate of 0.90 is not claimed as passed.

## Reopen criteria

Reconsider only if a narrowly scoped integration can run all three synthetic
scenarios without a second implementation of the A-share and capacity rules,
matches canonical outputs or classifies every residual difference, reaches at
least 0.90 coverage, and meets a reproducible performance threshold registered
before the benchmark. The integration ledger does not currently define a
numeric performance threshold. Until then, `native.position_replay` remains
the only registered backend.
