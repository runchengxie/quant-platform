# Incumbent requalification for portfolio construction

Language: English · [简体中文](incumbent-requalification.md)

`portfolio_backtester.incumbent_requalification` separates new-position entry from incumbent exit. It is useful when a candidate universe changes faster than the underlying investment signal.

- A new position must pass the current strict entry rules and rank within `entry_rank_limit`.
- An existing holding is rescored with current information. It may remain if it passes `hard_eligible` and ranks within the wider `exit_rank_limit`.

Leaving the entry universe does not automatically trigger a sale. An incumbent cannot remain indefinitely: it needs a current score, must pass hard eligibility, and must stay within the frozen exit buffer.

## Minimal example

```python
import pandas as pd

from portfolio_backtester import (
    IncumbentRequalificationPolicy,
    select_incumbent_requalified_portfolio,
)

candidates = pd.DataFrame(
    {
        "trade_date": ["2026-07-20"] * 4,
        "symbol": ["A", "B", "C", "D"],
        "selection_score": [0.90, 0.80, 0.70, 0.60],
        "industry": ["tech", "tech", "health", "industrial"],
        "hard_eligible": [True, True, True, True],
        "entry_eligible": [True, True, False, True],
    }
)

result = select_incumbent_requalified_portfolio(
    candidates,
    previous_symbols=["C"],
    policy=IncumbentRequalificationPolicy(
        portfolio_size=3,
        entry_rank_limit=3,
        exit_rank_limit=4,
        max_new_positions=1,
        industry_cap=2,
    ),
)

positions = result.positions
receipt = result.receipt.to_dict()
```

`C` is not eligible for a new entry, but can remain as an incumbent inside the exit buffer. A symbol with `entry_eligible=False` can never enter as a new position.

## Ranking universe

`rank_universe="hard_eligible"` is the compatibility default: Top-N ranks all currently hard-eligible symbols.

When the input contains full-market scores but new entries must come from a smaller strict candidate pool, set `rank_universe="entry_plus_incumbents"`. Ranking then covers current entry-eligible symbols plus previous holdings, with `hard_eligible` applied to both groups. Thus the entry Top-N ranks the eligible entry pool, while an incumbent outside that pool may remain within the exit buffer. Other symbols in the input do not take Top-N slots. The receipt reports the number ranked in `rank_universe_count`.

## Cash and replacement rules

Each selected symbol occupies a fixed slot:

```text
target_weight = 1 / portfolio_size
```

If hard exits outnumber the daily new-position budget, vacant slots remain cash. The selector does not rescale remaining holdings to full exposure. Set `allow_cash=False` to fail closed when the frozen policy cannot fill the portfolio.

During normal rebalances, at most `max_new_positions` may be added. The initial portfolio can fill up to `portfolio_size`. Once fully invested, a new candidate first challenges an incumbent outside the entry range but still inside the exit buffer, then a weaker incumbent still inside the entry range. A replacement must meet `min_score_improvement` and keep the resulting industry count within `industry_cap`.

## Inputs and limits

The default input columns are `trade_date`, `symbol`, `selection_score`, `industry`, `hard_eligible`, and `entry_eligible`. `IncumbentRequalificationConfig` maps caller-specific column names.

The selector returns target positions and an auditable receipt. It does not establish better returns and does not simulate T+1, partial fills, limit queues, or broker rejections. Before promotion, compare the policy with a baseline using the same frozen execution engine, cost model, and out-of-sample protocol.
