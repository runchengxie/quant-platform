# Evaluation orchestration

Language: English · [简体中文](evaluation.zh-CN.md)

`strategy_pipeline.pipeline.eval` coordinates metric calculation, portfolio replay, and result collection for an evaluation window.

It delegates scoring to `alpha_research.period_evaluation` and position, NAV, turnover, and exposure outputs to `portfolio_backtester`. This module standardizes inputs, call order, and the result-dictionary shape; it does not define strategy rules.

## Integration hooks

```python
from strategy_pipeline.pipeline.eval import (
    _build_period_positions,
    _evaluate_period,
)
```

These underscore-prefixed functions are internal hooks for the public pipeline's owner integration. Strategy repositories should use the `strategy_pipeline.control_plane` contracts rather than depending on these internal result fields.

`_evaluate_period` calculates evaluation metrics first, records portfolio and NAV outputs, then adds scored-data and exposure outputs. Position-building and NAV helpers delegate to `portfolio_backtester` implementations and pass through the configured `allow_live_fallback` policy. The function accepts optional permutation-test training and test frames.

## Empty evaluation window

When `test_df_full` is `None` or empty, `_evaluate_period` skips evaluation and returns the standard empty result structure. The result preserves numeric metric series, empty frames and date lists, and `None` for unavailable backtest statistics or positions. The caller can continue building the normal run summary without a separate missing-window schema.

The empty result shape is covered by `tests/orchestration/test_pipeline_eval.py`.
