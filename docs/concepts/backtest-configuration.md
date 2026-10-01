# Backtest Configuration Resolution

Language: English · [简体中文](backtest-configuration.zh-CN.md)

`portfolio_backtester.backtest_config.resolve_backtest_base_settings` normalizes shared backtest configuration that does not depend on a data provider. It handles:

- Benchmark symbols and comparison benchmarks
- Portfolio weighting, group limits, and selection tie-breaks
- Exit mode, exit-price policy, and fallback policy
- Costs, turnover, tradability fields, and long/short options
- Tear sheets and post-backtest processing switches

The function returns normalized run settings. Callers remain responsible for validating data fields, building execution models, and supplying the columns required for execution simulation. This keeps portfolio and backtest rule semantics in `quant-platform`, while a pipeline composes data, evaluation, and runtime configuration.

## Usage

```python
from portfolio_backtester.backtest_config import resolve_backtest_base_settings

settings = resolve_backtest_base_settings(
    backtest_cfg,
    eval_top_k=20,
    eval_rebalance_frequency="W",
    eval_transaction_cost_bps=10.0,
    label_horizon_days=5,
)
```

Explicit validation errors are reported through `SystemExit` and generally include the `backtest.<option>` prefix to help CLI callers locate the setting. Numeric conversions are not all wrapped, so malformed numeric values may also raise standard `TypeError` or `ValueError` exceptions.
