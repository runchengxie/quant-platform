# Minute-factor boundaries

This repository contains two minute-factor implementations. Check the module, input clock, and stock-day contract before using either one in research.

## Current research entry point

`alpha_research.minute_friend_factors` is the current definition for the friend-factor challenge. It generates DuckDB SQL only. It does not read files or choose a data provider.

The caller must provide a normalized minute-bar relation with:

- `trade_date` and `symbol` identifying each stock-day;
- a unique `bar_index` that increases across both the morning and afternoon sessions within a stock-day;
- `session_id` identifying the two sessions;
- `open`, `close`, and `volume` expressed in consistent units.

`friend_minute_feature_query` returns five volume-activity factors, three realized-variation factors, two intermediate variation measures, and minute-data diagnostics. Duplicate `bar_index` values are reported and cause the formal factor values for that stock-day to be null.

```python
from alpha_research.minute_friend_factors import friend_minute_feature_query

query = friend_minute_feature_query(
    relation="canonical_minute_bars",
    expected_bar_count=240,
)
```

`expected_bar_count` sets only the denominator for the coverage diagnostic. It does not fill missing minutes or reconcile feeds that start at 09:30 versus 09:31. The data-production layer remains responsible for retaining the provider, data tier, validity time, raw-partition hash, and build receipt.

## Earlier exploration module

`alpha_research.minute_factors` is an earlier exploration helper. `compute_volume_perc` divides a simplified continuous clock into buckets and does not split the trading day around lunch. As a result, some afternoon bars can fall into the final bucket.

Do not treat this module as the authoritative source for formal stock-day minute assets until session mapping, provider clocks, and coverage rules have been corrected. The friend-factor challenge uses `minute_friend_factors`.

## Checks before research or backtesting

Before using minute factors in formal discovery or a backtest, check:

- whether each stock-day key is unique;
- whether `bar_index` is increasing, continuous, and duplicate-free;
- whether morning and afternoon bars match the source's actual clock;
- missing bars, invalid prices, and non-positive volume;
- provider changes and the 240-versus-241-bar difference;
- whether each factor is available before its signal-generation time.

Minute factors produce research features only. Sample selection, labels, model training, portfolio construction, and execution costs belong to their respective modules.

Language: English · [简体中文](minute-factors.md)
