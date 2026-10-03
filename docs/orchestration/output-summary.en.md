# Run summary sections

Language: English · [简体中文](output-summary.md)

`strategy_pipeline.pipeline.output_summary_sections.build_run_summary_sections` turns a run context and artifact references into structured, serializable summary sections.

```python
from strategy_pipeline.pipeline.output_summary_sections import build_run_summary_sections

summary = build_run_summary_sections(context=context, artifacts=artifacts)
```

The result includes sections for the run, data, dataset, signals, model details, universe, labels, splits, evaluation, backtest, final out-of-sample results, diagnostics, positions, live outputs, promotion sidecar, quality, fundamentals, industry, and walk-forward checks.

This helper organizes reported values; strategy logic, feature definitions, data providers, credentials, and execution policy remain with the owner repository. It uses execution-model and simulator-configuration descriptions from the public `portfolio-backtester` interfaces rather than reimplementing those domain models.
