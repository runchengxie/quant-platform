# Runtime kernel contracts

`quant-platform` owns the deterministic runtime that turns research targets into
orders, fills, ledger updates, and immutable evidence. Runtime-local typed events
are an internal control-flow mechanism; repositories exchange only versioned
contracts and immutable artifacts.

Execution-aware runs must record data vintage, calendar version, strategy and
engine versions, execution policy, cost model, and random seed in the run
manifest. Market data views enforce that every record was effective no later than
the knowledge cutoff. Order events are accepted only when they follow the typed
lifecycle and cannot overfill or mutate a terminal order.

Pre-trade rules return `PASS`, `REJECT`, or `ADJUST`. Rules execute in a stable
order, adjustments feed the next rule, and rejection stops the pipeline. Runtime
events describe the trading-day lifecycle without creating a cross-repository
event bus. Immutable evidence records what happened; a future checkpoint feature
would separately capture mutable resume state.
