# Cost evidence

`quant_platform.backtest.costs` provides an additive `cost_evidence.v1` contract.
It describes source costs without changing historical accounting or estimating
missing components. Importing this module does not import an execution simulator.

```python
from quant_platform.portfolio import CostBreakdown

# Synthetic aggregate example. Revision identifies the source implementation
# and configuration together; source_id identifies the originating run/leg.
evidence = CostBreakdown(86, 100).to_cost_evidence(
    source_id="example-run:entry-leg",
    source_revision="example-source-and-config-v1",
)
assert evidence.total == evidence.unallocated_total == 186
assert evidence.components.commission is None
payload = evidence.to_mapping()
```

`CostBreakdown.to_cost_evidence` deliberately treats every component as unknown,
including when optional constructor fields contain zeros. Its aggregate buckets
remain in `raw_buckets`. It cannot recover per-order minimum commissions or
separate spread, tax and impact from those buckets. This conservative adapter
also accepts component-built breakdowns without upgrading their provenance.
A producer that can independently identify components can construct
`CostEvidence` with `CostComponents` directly.

`ExecutionSimResult.to_cost_evidence` and
`ExecutionAdjustedNavResult.to_cost_evidence` return one record per source fill.
Call them with the same explicit source arguments (and optional `currency`).
Each record links to a zero-based row locator in that result's original fills
frame. Preserve the frame with the evidence, and do not reuse a source ID for
a reordered or different run. Missing or null source columns stay unknown.
The source transaction total and all available `cost_*` buckets are retained;
no fee model is replayed. Empty fills produce an empty tuple.

Every record declares its stage, scope, accounting owner, amount unit, optional
currency and source revision. `actual_fill_model` means a simulated filled
execution, not a real broker charge. `planned_estimate`, `aggregate_estimate`
and `broker_actual` are also supported by the neutral contract; constructing
broker evidence requires independently obtained broker sources. The adapters
never promote preview quotes to booked fills.

For dated cumulative fees, the group preserves the producer's order/day key,
rule revision, before/after notionals, order ID, market and schedule interval.
The revision must identify the actual source configuration as well as code.
Noncumulative quotes use a fill scope: the presence of an order/day-shaped key
alone does not establish that a minimum is accrued across that group. No group
is fabricated when the source omits one. These are simulator rules, not a claim
that all brokers or markets group charges identically.

The validator enforces finite amounts and
`total = sum(known components) + unallocated_total`. The residual can be signed;
it preserves source inconsistencies instead of silently rewriting a historical
total. A nonzero residual is a reason to inspect the source. Completeness is
computed from available components: `unknown`, `partial` or `source_identified`.
A known zero differs from `None`. Component names describe source implementation
buckets; `temporary_impact` does not establish measured economic impact.

The simulator does not model unfilled opportunity cost. Its raw zero is retained,
while normalized opportunity cost is `None` and status is `not_modeled`.
Consequently its component completeness is `partial` even when all booked cost
components are known. Independent modeled opportunity evidence must use the
`economic_opportunity` accounting owner; it must not be silently added to a cash
charge. This contract does not estimate a counterfactual benchmark or provide a
cost-to-cash reconciliation beyond its own component sum. Historical result
frames, ledgers, totals and bundle formats remain unchanged.
