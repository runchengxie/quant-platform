# Portfolio execution profiling record

## Pre-registered method

This profiling pass uses deterministic synthetic inputs only. It does not load
production data. No Rust kernel is selected until the baseline measurements and
profiles are recorded.

Run `scripts/benchmarks/portfolio_execution_profile.py` once per workload with
five timed repetitions. The fixed fixture has 120 business sessions, 120
symbols, 320 target rows across four rebalances, deterministic prices and
liquidity (`amount = 200000 + (symbol_index % 13) * 175`,
`medadv20_amount = 400000 + (symbol_index % 13) * 350`), and explicit
market-rule columns. This liquidity range allows the 100-share round lot to
fill while retaining multi-day partial fills. The script reports workload
dimensions, output-frame sizes, the SHA-256 digest of canonical result frames,
median wall time, process peak RSS, software versions, and cumulative Python
profile samples. Linux `ru_maxrss` is reported in KiB.

The workloads are:

1. `daily-ledger`: execution-adjusted NAV with orders, fills, daily cash and
   positions, round lots, T+1, limit and listing-status fields.
2. `order-matching`: capacity-based rebalance order planning, daily liquidity
   caps, partial fills, and cancel/deadline paths.
3. `scenario-sweep`: twelve capacity runs over four participation rates and
   three buy deadlines, with a digest covering all outputs.

The run environment and exact output digests are recorded below after baseline
execution. A Rust kernel is eligible only if profiling isolates a stable
primitive-array kernel that can plausibly deliver at least 2x repeated median
end-to-end speedup in its dominant workload. The Python path remains the
reference and required fallback. Any candidate must pass parity tests before
implementation and meet the same gate after repeated benchmark runs.

## Baseline results

Pending execution of the pre-registered workloads.
