# USD price ledger

Stage A supports diagnostic, long-only cash-equity and ETF accounting with USD
cash. Quantities remain fixed between modeled transactions. Price and FX changes
cause natural weight drift. Dividends, splits, futures, margin, shorts, foreign
cash balances and total returns are unsupported.

## Synthetic example

```python
from datetime import UTC, datetime, timedelta
from decimal import Decimal as D

from research_contracts import ArtifactRef, ResearchClock
from portfolio_backtester.usd_ledger import run_usd_price_replay
from portfolio_backtester.usd_ledger_models import (
    USDInstrument,
    USDPriceObservation,
    USDRebalanceDecision,
    USDReplayConfig,
    USDReplayRequest,
)


def t(day, hour=0):
    return datetime(2026, 1, day, hour, tzinfo=UTC)


ref = ArtifactRef("synthetic-prices", "a" * 64)
instrument = USDInstrument("example", "etf", "USD", 1, "synthetic-session.v1")
prices = tuple(
    USDPriceObservation(
        "example",
        time,
        time,
        value,
        "currency_per_share",
        ref,
        "verified",
        "synthetic-session.v1",
        True,
    )
    for time, value in ((t(1), D("10")), (t(1, 1), D("10")), (t(3), D("20")))
)
clock = ResearchClock(
    "UTC",
    t(1),
    t(1),
    t(1),
    t(3),
    "synthetic-next-mark.v1",
    "synthetic.v1",
    t(1, 1),
    t(1, 1),
    t(1, 1),
)
config = USDReplayConfig(
    D("100"),
    "fractional",
    D("0"),
    D("0"),
    D("0"),
    timedelta(days=5),
    timedelta(days=5),
    {},
)
request = USDReplayRequest(
    (instrument,),
    prices,
    (),
    (USDRebalanceDecision("decision-1", clock, {"example": D("0.5")}, {"example": t(1, 1)}),),
    (t(1), t(2), t(3)),
    config,
)
result = run_usd_price_replay(request)
assert list(result.daily.nav_usd) == [D("100"), D("100"), D("150")]
assert result.holdings.iloc[-1].quantity == D("5")
assert result.daily.iloc[-1].cash_usd == D("50")
```

The initial 50% target buys five shares. It does not rebalance every valuation:
when the price doubles, cash remains 50, position value becomes 100 and NAV is
150. The fixture uses invented timestamps and prices, not real session evidence.

## Public interfaces

- Records: `portfolio_backtester.usd_ledger_models` defines `USDInstrument`,
  `USDPriceObservation`, `USDModeledExecutionPrice`, `USDFXObservation`, `USDRebalanceDecision`,
  `USDReplayConfig`, `USDReplayRequest`, `USDReplayResult`, `USDValidationError`.
- `validate_usd_request(request: USDReplayRequest) -> None` in `usd_ledger_inputs`.
- `select_usd_price(request: USDReplayRequest, instrument_id: str, at: datetime,
  *, execution: bool = False) -> USDPriceObservation`.
- `select_usd_modeled_execution_price(request, instrument_id, at)` selects only
  an exact caller-scheduled UTC open from `USDReplayRequest.modeled_execution_prices`.
- `select_usd_fx(request: USDReplayRequest, currency: str, at: datetime)
  -> tuple[Decimal, USDFXObservation | None]`.
- `value_usd_book(quantities, cash, local_prices, usd_per_local)` in
  `usd_ledger_accounting` returns Decimal position value and NAV.
- `settle_usd_rebalance(quantities, cash, desired_quantities, local_prices,
  usd_per_local, instruments, config, *, execution_ids)` returns quantities,
  cash and modeled transactions. Only the supplied batch IDs change.
- `run_usd_price_replay(request: USDReplayRequest) -> USDReplayResult`.
- `write_usd_price_replay_bundle(output_dir: Path, *, result: USDReplayResult,
  run_id: str, research_clock: ResearchClock, producer: Mapping[str, Any],
  configuration_sha256: str, input_refs: Sequence[Mapping[str, Any]])
  -> BacktestBundleManifest` in `usd_ledger_bundle`.

## Units, clocks and sizing

Use finite Decimal values for all economic fields and aware UTC timestamps.
Instrument currency is explicit; price unit is `currency_per_share`. FX unit is
`quote_per_base`. Each foreign currency selects one direct or inverse USD pair:
GBPUSD 1.25 means USD per GBP is 1.25; USDHKD 8 means USD per HKD is 0.125.
USD has an explicit identity conversion. There is no triangulation or provider
fallback. A series has one immutable source reference and no duplicate bar times.

Valuation selects the newest mark whose bar and availability times are at or
before the event, bounded by configured price/FX maximum age. Every held asset
needs marks. Unused assets and all-cash runs do not. Raw FX direction, source hash,
units, bar time and availability time remain in detailed evidence.

Every decision includes its own ResearchClock and an execution schedule covering
the instrument universe, including zero targets for liquidation. Windows cannot
overlap. Execution is strictly after decision time, requires an exact eligible
price timestamp with matching session-policy identity, and rejects assumed
availability. These flags are caller attestations; the ledger is not a market
calendar service and cannot establish their truth. Date-only historical CSVs
cannot supply verified execution marks. A caller may instead wrap an observed
daily open as a modeled reference with an explicit assumed session timestamp;
that remains a research diagnostic. An assumed conservative lag may support
valuations when explicitly enabled, but cannot make a carried close eligible.

For research-only next-open replay, set `allow_modeled_execution_prices=True`
and provide a `USDModeledExecutionPrice` for each changed instrument and its
exact scheduled execution timestamp. This separate input records the caller's
local session date, assumed UTC open, reference price, immutable source, session
policy and model ID. The timestamp must match a decision's execution schedule.
The platform does not infer the local session date from UTC or verify exchange
calendar correctness. In this mode, a missing exact reference is an error; the
ledger does not fall back to a close or verified observation. The reference is
not a broker fill and does not establish market availability; transactions
carry `execution_evidence_kind="modeled_reference"` and
`execution_eligible=False`, while orders and fills remain empty.

Modeled buys apply positive signed slippage to the reference price and modeled
sells apply negative signed slippage. Commission and FX costs remain separate;
the replay and bundle publisher reconcile the resulting cash, inventory and
NAV. An FX observation with `availability_basis="assumed_market_session"` is
accepted only when both `allow_assumed_availability` and
`allow_modeled_execution_prices` are enabled. This is an explicit FX timing
assumption, not proof of a tradable conversion quote. The verified execution
selector remains unchanged and cannot select a modeled reference.

Desired quantities freeze from pretrade NAV and available marks at decision time.
Events execute chronologically. Same-time sells settle first, then affordable buy
increments scale proportionally including costs. Future sells cannot fund earlier
buys; a scaled batch is never retried silently. Commission and FX costs are
separate fractions of reference USD notional. In modeled-reference mode,
slippage is reflected in the signed execution price and reconciled separately as
a cost; in verified mode the existing slippage cost treatment is retained. USD
assets incur no FX fee.

Fractional increments round down to 1e-12 shares. Integral increments round down
to each positive integer instrument lot; partial sells also round down, while a
full liquidation may sell a held odd lot. USD cash is retained with zero interest.
Spot conversion is modeled per transaction; there is no foreign cash account.

## Reconciliation and publication

Daily NAV equals cash plus marked inventory. Between mark updates, local P&L is
`(P_new-P_old)*F_old*q` and FX P&L is `P_new*(F_new-F_old)*q`, on quantities held
before the update. Costs reduce NAV once. Arithmetic uses local Decimal precision
50; reconciliation permits only relative 1e-45 arithmetic roundoff.

The replay retains a sequenced event log: mark updates include pre-update
quantities and old/new price/FX; decisions retain pretrade NAV; modeled
transactions and valuations reference their event sequence. Target records
retain decision NAV and complete selected-mark metadata.

The publisher independently replays these events and recomputes both P&L
components, target sizing, cash, inventory, costs, holdings and source lineage
before checking root bounds and using the existing immutable, hashed writer.
Aggregate Parquet economic values and detailed JSON economic values are Decimal
strings. This preserves precision; consumers must parse Decimal explicitly.
The existing generic bundle reconciliation also produces its usual numeric
receipt; `diagnostics.json/usd_reconciliation` records the stricter USD checks.

The root clock starts at the first decision and ends at the final valuation;
its execution bounds cover the run. Per-decision clocks remain authoritative
for later decisions. The root information cutoff does not authorize all later
inputs. An all-cash run may use a root decision at or before its first valuation.
Lineage is nonempty even for an all-cash run, e.g. the configuration artifact.

Results are `diagnostic` and `usd_price_nav`, with `orders_submitted=False`.
Orders/fills are empty and lifecycle capability is false. Modeled transactions
are separate evidence, not broker fills. The execution-aware multi-decision
restriction remains unchanged. Report cumulative return, drawdown and
calendar-time CAGR (365.25 days/year); a single valuation has undefined CAGR.
Sharpe is omitted until an explicit sampling policy exists.

Research consumers must pin a reviewed reachable platform revision and supply
released datasets and versioned signal schedules. Strategy choices, provider
acquisition and runtime orchestration remain outside this platform. Total-return
accounting and futures settlement require separate capabilities and plans.
