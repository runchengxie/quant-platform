# Account feedback and execution research design

The user authorized progressing account feedback, paired execution paths, explicit
cost coverage and persistent impact research together on 2026-11-07.

## Approaches

Extending the existing minute simulator preserves its accounting and T+1 semantics.
A second simulator would duplicate those rules. Modifying Rust first would leave
the historical Python research caller disconnected. Use the first approach; keep
Engine and Runtime responsibilities unchanged unless integration demonstrates a gap.

## Interfaces and boundaries

Add an opt-in decision callback to minute execution, invoked at decision time with
copies of cash, actual inventory, raw marks, receivables and live orders. Returned
complete weights are frozen until entry; no observation at or after decision may
leak into the callback. None means preserve live orders. Default replay is unchanged.
Synchronous cancellation remains explicit; delayed exchange acknowledgements are
not certified by this interface. Holdings omitted from candidates remain visible.

Add a separate linear transient/permanent impact research primitive, measured in
price per share, driven by actual signed fills and elapsed seconds. Fill prices
use pretrade state plus half the current trade increment; this preserves splitting
at identical timestamps and nonnegative flat-market round trips for nonnegative
linear coefficients. State can be serialized/restored. It is uncalibrated and must
not be silently added to existing costs or presented as a market-response estimate.

Strict participation cost coverage rejects missing liquidity and orders beyond
the calibration range; legacy behavior is available only through explicit policy.

Research runs paired baseline and feedback policies under predeclared execution
scenarios, independent accounts and matching external bars, retaining failures.
Performance uses execution-ledger daily NAV and differences of paired returns.
No future probability, alpha certification or new untouched sample is claimed.

## Acceptance

Partial fills change later decisions; live orders can be preserved without duplicate
submission; future-bar mutations preserve prior decisions; T+1 remains daily.
Missing held marks fail clearly. Costs are charged once. Impact survives recovery,
decays only forward in time, and does not reward mechanical splitting or round trips.
Real data remains read-only and generated outputs remain outside source repositories.
