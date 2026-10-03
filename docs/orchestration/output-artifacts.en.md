# Run artifacts

Language: English · [简体中文](output-artifacts.md)

`strategy_pipeline.pipeline.output_artifacts` writes configured datasets, features, signals, evaluation results, backtest outputs, and diagnostics under a run directory. `write_run_artifacts(context=...)` returns a mapping of artifact names to paths or summaries.

```python
from strategy_pipeline.pipeline.output_artifacts import write_run_artifacts

artifacts = write_run_artifacts(context=context)
```

The module handles file formats, paths, and the artifact-path inventory. Owner packages provide data access, signal calculation, portfolio rules, and execution models. Backtest and position artifacts use public `portfolio-backtester` interfaces; signal artifacts use the public `quant-market-research` interface.

The caller supplies the run context, and configuration controls which outputs are written. The function does not read credentials, generate strategy signals, or change portfolio logic.

An owner may provide `weekly_basket_performance_path`. The pipeline then records that path in the returned artifact inventory; it does not read the file, scan the run directory, calculate performance, or import strategy code. If omitted, the field is `None`.
