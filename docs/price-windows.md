# Convert research price windows

Language: English · [简体中文](price-windows.zh-CN.md)

Use `quant_platform.prices.convert_price_window` to express eligible raw quotes
in raw, supplier-factor HFQ, or as-of PIT-QFQ units. It converts research inputs;
Core owns fills, shares, fees, corporate actions and cash accounting.

```python
import pandas as pd
from quant_platform.prices import convert_price_window

quotes = pd.DataFrame(
    {
        "symbol": ["AAA", "AAA", "AAA"],
        "trade_date": ["2024-01-02", "2024-01-03", "2024-01-04"],
        "available_at": ["2024-01-02T08:00Z", "2024-01-03T08:00Z", "2024-01-04T08:00Z"],
        "close": [100.0, 50.0, 60.0],
    }
)
factors = quotes[["symbol", "trade_date", "available_at"]].assign(adj_factor=[1, 2, 2])
window = convert_price_window(
    quotes,
    factors=factors,
    basis="pit_qfq",
    as_of="2024-01-04T08:00Z",
    source_ref="synthetic:quotes-v1",
    factor_source_ref="synthetic:factors-v1",
    price_columns=("close",),
)
assert window.prices.close.tolist() == [50, 50, 60]
```

## Inputs and observation time

Both tables require `symbol`, `trade_date`, and `available_at`. Quotes also
require each requested price field (OHLC by default). Factors require
`adj_factor`. RAW needs only quote data and `source_ref`; adjusted modes also
need factors and `factor_source_ref`. References are nonempty caller identifiers
for the source/vintage, ideally immutable manifests or content hashes.

`trade_date` is a naive midnight calendar date. `as_of` and every `available_at`
are timezone-aware timestamps normalized to UTC; the market-date horizon is the
Shanghai date of `as_of`. A date alone or a numeric timestamp is rejected.
Quote and factor observation clocks are independent. An exact-cutoff observation
is eligible. Multiple observed revisions are supported; the latest eligible
observation for each security/date is selected before joining. Duplicate
security/date/observation-time rows reject. Future market dates and later
observations are excluded. The output retains selected rows in input order and
preserves their index, while normalizing dates/clocks.

The converter validates declared clocks; it cannot authenticate when a vendor
actually published a value. Do not give reconstructed latest history invented
old availability timestamps. A latest factor table filtered by trade date alone
does not prove PIT safety. Retain real observation vintages and independent
source audit evidence before claiming historical availability.

## Units and missing values

| Basis | Formula for historical session s | Meaning |
| --- | --- | --- |
| `raw` | raw price | Original share-price units |
| `hfq` | raw price × F_s | Unnormalized supplier-factor scale |
| `pit_qfq` | raw price × (F_s / F_t) | Each security's latest eligible factor anchor at/before the horizon |

HFQ does not promise an unchanged initial historical price. Supplier definitions
and factor direction must match this multiplicative contract. PIT's anchor may
be newer than the last available quote during a halt, but no quote is fabricated.
When the current quote's factor is the anchor, its converted price equals raw.

An unavailable/missing required historical factor, empty quote window, invalid
factor, nonpositive/nonfinite observed price, or invalid converted nonmissing
price raises `ValueError`. No factor=1 fallback or price forward filling occurs.
Null quote prices remain null. A factor must be positive and finite. PIT ratios
are computed before multiplying to avoid unnecessary intermediate overflow.
Extra quote columns, including volume and amount, are copied unchanged.
Known nonprice fields cannot be selected as `price_columns`.

`PriceWindow` contains `prices`, `basis`, UTC `as_of`, source references and
`anchors`. PIT anchors expose `symbol`, `trade_date`, `adj_factor`, `available_at`;
RAW/HFQ expose an empty anchor frame with the same columns. Source frames are
not mutated. The wrapper is frozen, but its independent DataFrames remain
mutable; it is not an immutable artifact or an execution request. As with pandas deep copies, nested Python objects in extra columns remain shared and must not be mutated through the result if source isolation is required.

## Use with research and accounts

Scale-invariant momentum and moving-average comparisons agree between HFQ and
QFQ under identical factors and missing-data handling. Homogeneous price-level
indicators can be converted with the same anchor; nonlinear indicators are not
generically divided by a factor.

Execute and value raw-share accounts with raw prices and explicitly audited
corporate actions. Do not add dividend/share events to adjusted-price returns.
Adjusted total returns equal raw-account returns only with matching
reinvestment, tax, settlement timing, execution-price and cost assumptions.
Delayed payments or cash retained instead of reinvested can produce legitimate
differences. This interface does not certify event completeness, tradability,
account entitlements, historical fees or raw suspension valuation support.
