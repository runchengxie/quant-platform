# Daily Microstructure State Design

## Goal

Add a public, strategy-agnostic measurement layer that converts one complete packed L2 trading day into a stable daily state without changing the existing event-window model or introducing private alpha definitions.

## Scope

The first vertical slice exposes a pure NumPy API over the existing packed structured arrays (`order`, `trade`, `snap`) and `prev_close_cent`. It returns named scalar measurements suitable for baselines, downstream research, or later model fusion.

The initial measurements are deliberately low-level and interpretable:

- event counts and observation duration;
- signed trade flow and trade amount;
- price-impact proxies from absolute return per turnover;
- robust spread, depth, and L1 imbalance summaries;
- realized variance and upside/downside semivariance from snapshots;
- early-versus-late path decomposition and close-to-last-observation recovery.

No threshold selected from a target sample, alpha direction, factor ranking, cross-sectional normalization, or private trading rule belongs in this public module.

## API

Create `ticknet.eventstream.daily` with:

```python
def aggregate_day(
    order: np.ndarray,
    trade: np.ndarray,
    snap: np.ndarray,
    prev_close_cent: float,
) -> dict[str, float]: ...
```

The function accepts the existing dtypes from `eventstream.config`, is deterministic, avoids mutation, and returns the same complete key set for empty or non-empty inputs. Missing or non-finite measurements use `0.0`; a separate `*_observations` count identifies whether a statistic had data.

The module may contain small private helpers and constants, but must not import Torch, pandas, or a research-only package. Public names are exported through `ticknet.eventstream`.

## Measurement semantics

All event counts are counts in the supplied day, not extrapolated rates. `event_rate_per_hour` uses the min/max event timestamps and is zero when the observed duration is non-positive. Signed trade flow uses `side` values after normalizing positive to buy and negative to sell; unknown sides contribute to amount but not signed flow. Snapshot price returns use consecutive positive prices, and the first return is excluded. Realized variance is the sum of squared returns; upside and downside semivariances sum squared positive and negative returns separately.

Price impact is `sum(abs(snapshot return)) / sum(snapshot turnover)` after converting turnover from cents to the same notional scale used by the packed data; it is zero when turnover is unavailable. Spread is the relative L1 ask/bid spread in basis points. L1 imbalance is `(bid_vol - ask_vol)/(bid_vol + ask_vol)`.

Early/late path values use the median observed event timestamp as the split; they report signed trade amount in the two halves and the snapshot return from the first observation to the split and from the split to the last observation. Recovery is the signed change from the last snapshot to the final observed price, with the final observed price chosen from the latest timestamp across trade, order, and snapshot streams. It is a descriptive measurement, not a claim of permanent impact.

## Data flow

```text
packed day arrays
      -> aggregate_day()
      -> named daily state dict
      -> future EWMA / VQ-code / model-fusion consumers
```

The first slice does not materialize a new on-disk artifact and does not alter `L2WindowDataset`. A later change can add a materializer once the state schema has been validated on real data.

## Compatibility and constraints

- Keep `ticknet.eventstream` importable without optional Torch installation.
- Preserve all existing eventstream and simulator behavior.
- Keep the public package strategy-agnostic per `AGENTS.md`.
- Do not add dependencies.

## Verification

Tests will use small deterministic structured arrays built from the existing contract dtypes. They will cover non-empty aggregation, empty inputs, unknown trade side handling, timestamp ordering across streams, and no input mutation. The focused test file, microstructure test suite, `ruff`, and full `pytest` will be run before completion.
