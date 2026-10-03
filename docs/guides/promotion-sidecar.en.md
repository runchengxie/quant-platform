# Promotion-evidence execution sidecar

Language: English · [简体中文](promotion-sidecar.md)

`portfolio_backtester.promotion_sidecar` simulates fills, orders, positions, cash, and constraint events from target positions and historical prices. It provides tradability evidence for a research promotion review; it does not replace the execution engine's live order submission or risk controls.

```python
from portfolio_backtester.promotion_sidecar import (
    PromotionSidecarConfig,
    simulate_promotion_sidecar,
)

result = simulate_promotion_sidecar(
    positions,
    pricing,
    PromotionSidecarConfig(enabled=True),
)
```

The result exposes `events`, `orders`, `fills`, `positions`, `cash`, and `violations`. An orchestration layer can persist them as run artifacts. The sidecar can be disabled; when enabled, it requires pricing data for non-empty positions. Capacity limits can leave orders partially filled, so target weights must not be presented as executed holdings.
