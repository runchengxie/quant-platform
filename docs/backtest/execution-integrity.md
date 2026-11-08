# Recorded-fill integrity and pooled-account exploration

`quant_platform.analytics.execution_integrity.fill_prefixes` reconstructs cash and
raw integer shares from explicit recorded fills, grouped at identical UTC
nanosecond clocks. It requires unique source-record IDs, positive quantities and
prices, nonnegative fees, finite Decimal-compatible values and a long-only book.
`compare_prefixes` retains the first and every later divergent event clock, even
when final balances agree. These are reconstructions from fill evidence, not
observations of an upstream engine's hidden intraday account cache. Admission,
queue, T+1 and fees still need their owner evidence and separate daily ledger checks.

Arithmetic uses an isolated 64-significant-digit Decimal context with inexactness
trapped as ValueError. Caller precision does not silently alter comparisons; extreme
inputs outside exact arithmetic capacity are rejected rather than rounded away.

`quant_platform.portfolio.sleeves.pool_sleeves` accepts complete long-only target
frames and fixed budget fractions totaling at most one. All sleeves must declare
the same entry and decision schedule. The result goes through one existing minute
owner, consuming one volume budget and one impact state. This represents a pooled
cash account, not independently funded brokers sharing a venue. It provides neither
sleeve fill allocation, crossing attribution, fairness nor sleeve performance.

`exit_wealth` reports cash, receivables, residual quantities, supplied mark prices
and clocks, valuation time and freshness bound. Stale/missing held marks leave
marked wealth unknown; unsold shares never become realized cash. Conditional
cash-realized wealth is present only with zero inventory and receivables. Marked
wealth does not promise an executable liquidation price.

Run the synthetic real-backend experiment with a content-pinned engine:

```sh
python -m scripts.benchmarks.execution_integrity --binary /releases/engine \
  --sha256 <binary-digest> --output /data/integrity-report.json
```

The zero-spread, matching-clock roundtrip must agree in fill-prefix and actual
daily cash, quantities, commission, marked positions and NAV. A changed valuation
quote must produce exactly the declared first-day value/NAV difference. IOC partial
execution must retain its specific quantity/cash/fee differences against the Python
parent that continues over later bars. Hand-calculated complete signatures prevent
unrelated divergences from passing merely because some difference was expected.
These quote sizes are synthetic liquidity, not historical volume or real capacity.

The pooled-account probe compares equal total starting cash: two independently
simulated accounts each consume a bar budget, while their pooled target uses one.
It illustrates the assumption boundary without certifying independent broker
coordination or real-market impact parameters.
