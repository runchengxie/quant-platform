# Generic multi-sleeve portfolio construction

Language: English · [简体中文](sleeve-portfolio.md)

`portfolio_backtester.sleeve_portfolio` turns upstream-scored candidates into target positions. It owns generic portfolio mechanics; strategy names, research assumptions, and model versions remain with the upstream strategy owner.

The public interface includes:

```python
from portfolio_backtester.sleeve_portfolio import (
    QuotaSleeveSpec,
    RankBufferedSleeveSpec,
    SleevePortfolioSpec,
    build_sleeve_positions,
    compute_position_changes,
    compute_position_exposure,
)
```

Use `QuotaSleeveSpec` for group-based quotas such as themes or industries. Use `RankBufferedSleeveSpec` for entry and exit ranks, optional group caps, and a daily replacement limit. `SleevePortfolioSpec` combines these mechanisms with overlap and weight rules.

Strategy owners freeze their own parameters upstream and convert them explicitly into these generic specifications. The shared module must not embed strategy identities or their parameter constants.

The output follows the core `positions_by_rebalance` fields: `rebalance_date`, `entry_date`, `symbol`, `weight`, and `side`. It also carries `leg`, `signal`, `rank`, and score/group description columns used by the input specifications.

`compute_position_changes` and `compute_position_exposure` describe positions already constructed; they do not calculate alpha. Execution capacity, orders, fills, and the daily ledger remain with `execution_sim` and position replay.
