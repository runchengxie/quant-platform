# Daily execution consumers

[简体中文](engine-daily.zh-CN.md)

Platform 0.3.0 consumes Core 0.3.0 and SDK 0.3.0 from the same merged Engine revision `ad0895f1c2015eb31bd364b40741b0f7cd6e0048`. The daily financial owner, diagnostic leg/period accounting, legacy trade accounting, fee models and result classes live in Engine. Platform selects targets, resolves provider calendars at its existing consumer boundary, calculates research statistics and publishes bundles.

## Legacy research workflows

Existing native, sequenced, position and top-k arguments remain available. The direct daily and position wrappers return the original Engine-owned result classes. All raw financial tables and the eight `UnifiedLedger` fields come from that owner. Platform restores the original period-return research formulas, including distribution, drawdown timing, exit lag, yearly and H1/H2 statistics. It preserves the eight financial period aggregates and schema/config/period/skipped metadata.

These historical statistics describe historical owner returns. A carried mark may make those raw returns unsuitable as supported valuation evidence. They are not a substitute for the neutral product's conservative summary. Legacy APIs also retain their original partial enforcement of listing/capacity options; the strict neutral profile rejects unsupported combinations. Eligibility-window end is not an observed delayed-fill deadline.

## Explicit neutral requests

`quant_platform.backtest.engine_daily.build_daily_request` accepts already selected positions, pricing, an explicit `ExecutionCalendar`, research clocks and an owned `ExecutionSimConfig`. It translates dates and exact selectors without fetching calendars, generating targets or adding a default liquidity column. `run_daily` dispatches Engine and adds the separately scoped research statistics.

`quant_platform.backtest.engine_clocks.to_execution_clocks(value: ResearchClock | Mapping[str, Any]) -> ClockSet` uses exact string UTC nanoseconds. Entry is the later supplied eligibility bound. Available/effective/report times remain unknown when the research contract supplies no observation. Original native v1/v2 integer-clock contracts are unchanged.

## Canonical product results

```python
from quant_platform.backtest.engine_results import to_canonical_result

partial_view = to_canonical_result(product_result)
full_view = to_canonical_result(product_result, artifact_root=owned_output_directory)
```

The compatible signature is `to_canonical_result(result: ProductResult, *, artifact_root: Path | None = None) -> CanonicalBacktestResult`. The one-argument call consumes normalized evidence and does not invent a full ledger. An explicit trusted root allows relative raw-artifact URI, media type, SHA256 and schema validation before decoding the original eight owner tables. There is no current-directory lookup, network fetch, arbitrary import or evaluation of dtype text. Unknown schemas/dtypes and paths escaping the root fail closed.

A verified complete raw table set and complete valuation evidence are separate facts. `performance.net_return` comes from the conservative `daily_return`; incomplete opening or closing endpoints stay unknown. Original returns remain `raw_executed_return`, with explicit scope metadata. After a missing mark, the recovery interval remains unknown; the following fully observed interval can be supported again. The product summary is preserved, so unknown cumulative return never becomes zero or an old drop-na research statistic.

`metadata.product_result` preserves each available/unavailable table declaration and reason. An available empty table remains distinct from unavailable evidence. `metadata.full_owner_artifact_verified` records raw verification; `metadata.execution_aware` additionally requires supported complete valuation. Bundle publication rejects `execution_aware=False`. Multi-decision results still require a future per-decision clock bundle schema; the existing single-clock writer rejects them.

## Capabilities and compatibility

The raw Rust session adapter remains limited and is never given a fabricated unified ledger or a Python fallback. Explicit verified Rust conversion retains its original tables and `execution_aware=False`. Diagnostic period returns do not imply daily cash/fills or borrow/margin support. Corporate-action receivables remain available in raw owner tables; the historical cash-plus-position ledger representation does not establish full receivable reconciliation.

Aliases remain for at least two minor releases and until every recorded supported consumer migrates. Passing Platform and synthetic cohorts does not migrate pinned Runtime/Go/Python environments or old checkpoints. Those retain their entire original release closure. See the [C ownership map](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/engine-provider-c.json), retained [A](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/engine-provider-a.json) and [B](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/engine-provider-b.json) receipts, and [Engine daily contract](https://runchengxie.github.io/quant-backtest-engine/product/daily-inputs/).

## Receivable representation limit

When owner daily rows contain unpaid cash or stock receivables, the historical eight-table representation cannot express their complete wealth. The converter retains the verified raw daily/actions/holdings and all eight tables in `metadata.owner_result`, but leaves canonical daily/unified ledgers unavailable and sets `execution_aware=False`. `canonical_ledger_limitation` distinguishes unpaid from unknown receivables. Unknown or nonfinite receivables never become zero. Payment transfers remain exactly as reported by the owner; conversion adds no balancing cash and changes no performance or summary. This is a representation limit, not a newly inferred loss or financial failure.

The [consumer migration contract](../migration/provider-c-consumer.md) records the implementation and acceptance scope.
