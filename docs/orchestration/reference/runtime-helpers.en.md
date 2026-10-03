# Runtime helpers

Language: English · [简体中文](runtime-helpers.md)

`strategy_pipeline.pipeline.runtime` provides shared helpers for research runs:

- configure logging and resolve an optional log-file path;
- hash a configuration;
- convert a final holdout length and purge or embargo durations into sample steps;
- split training, test, and final out-of-sample dates.

Date-splitting and evaluation rules use public `quant-market-research` interfaces. Rebalance intervals are estimated through the public `portfolio-backtester` interface. This module does not read strategy configuration or access credentials or data providers.

```python
from strategy_pipeline.pipeline.runtime import config_hash, setup_logging

run_hash = config_hash(config)
log_file = setup_logging(config, default_log_file=run_dir / "run.log")
```
