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

Environment: Linux `6.18.52-1-lts`, x86_64, Intel Core i5-4690K at 3.50 GHz,
4 logical CPUs, 31 GiB system memory, Python 3.13.14, NumPy 2.2.6, and pandas
3.0.5. The profiler runs under `uv run` in the repository's locked environment.
Input and generated result files remain outside the repository.

| Workload | Dimensions and output | Median wall time | Peak RSS | Output SHA-256 |
|---|---|---:|---:|---|
| `daily-ledger` | 14,400 pricing rows, 320 positions, 119 daily rows, 352 orders, 1,831 fills | 2.699452 s | 207,752 KiB | `0ee0f9d7d3d5f74aabecc571dac9b1cf2b728ac73f562f02f79231de5469133c` |
| `order-matching` | 14,400 pricing rows, 320 positions, 352 orders, 1,837 fills | 0.382356 s | 199,628 KiB | `1778a72f9feae297d6b6b200d48a505521610e332af7380f338c7a70fa1b0380` |
| `scenario-sweep` | twelve configurations, 3,636 total orders, 19,269 total fills | 4.040868 s | 206,864 KiB | `6216141b4dce65d54de9b1930f7346545c6b8e11b5259d903b3a8617c985d1df` |

Each median is from five timed repetitions. Every repetition produced the same
result digest and frame inventory. The script profiles one additional run
with `cProfile`; those instrumented times are for relative call-stack ranking
only and are not included in the wall-time medians.

The largest self-time Python frame in the daily ledger sample was
`execution_sim/capacity.py::_table_float_at` at 0.267 seconds over 47,344
calls. Pandas `DatetimeIndex.get_loc` used 0.253 seconds over 102,593 calls.
The order-matching and sweep profiles show the same scalar lookup family, with
`_table_float_at` self time of 0.035 seconds and 0.349 seconds respectively.
Time is spread across pandas scalar indexing, date lookup, capacity checks, and
stateful order processing. No single primitive-array numerical kernel
dominates the end-to-end workloads.

## Decision

Do not add a Rust kernel in this phase. The measured profile does not identify
an isolated numerical kernel with a credible path to the pre-registered 2x
end-to-end median speedup. The observed cost comes from repeated scalar
DataFrame/date lookups interleaved with stateful order and cash decisions.
Moving that path into Rust would require migrating the order lifecycle and
ledger state as a unit, beyond one narrow kernel. The Python implementation
remains the required reference. The benchmark and exact output digests are
retained so a later, broader Python data-layout change can be measured against
this baseline.
