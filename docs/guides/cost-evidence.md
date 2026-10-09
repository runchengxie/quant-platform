# Cost evidence and capacity

Signed implementation shortfall accounts for executions, unfilled opportunity
cost and explicit fees against requested decision notional. Favorable execution
may have negative shortfall. Existing non-negative v1 cost calibration is unchanged.

```python
import json
from pathlib import Path
import pandas as pd
from portfolio_backtester.shortfall import Fill, OrderCost, order_shortfall
from portfolio_backtester.tca_evidence import summarize_tca

rows = [
    order_shortfall(
        OrderCost(
            str(i),
            f"2024-01-0{i + 2}",
            "buy",
            10.0,
            100.0,
            (Fill(60.0, 11.0),),
            5.0,
            12.0,
            f"2024-01-0{i + 2}T15:00:00Z",
        )
    )
    for i in range(2)
]
evidence = summarize_tca(
    pd.DataFrame(rows), group_cols=[], min_observations=2, min_coverage=0.5, seed=7
)
Path("/external/data/cost-evidence.json").write_text(json.dumps(evidence))
```

This constructed case has 145 cash shortfall (60 execution, 80 opportunity, 5 fee)
and 1450 bp total. Requested/filled notionals in this contract use decision price,
so coverage measures filled quantity. Supply the unfilled benchmark and its
timezone-aware timestamp for every partial or zero-filled order.

The v2 report records requested-notional-weighted means, unweighted empirical
median/P95, completion coverage and a seeded 95% date-block bootstrap interval
(500 resamples by default). Fewer than two dates leaves uncertainty unavailable.
Caller-specified sample/coverage requirements control recommendation availability;
none are universal thresholds. A recommendation never promotes a cost model.

The capacity CLI accepts `--cost-evidence PATH` and optional
`--cost-evidence-sha256 SHA256`. Its report records `missing` or
`available_not_promoted`: evidence is not applied as a new production cost rate.
Evidence groups must cover the order profiles/scales being interpreted; small
liquid orders cannot calibrate large illiquid trades.

The payload checksum detects accidental modification; it is not producer
authentication. For trusted provenance, check the external artifact digest from
the authoritative owner manifest. Reports can preserve favorable signed values
without substituting them into the old non-negative cost assumptions.
