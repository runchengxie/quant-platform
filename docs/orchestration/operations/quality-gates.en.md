# Quality gates

Language: English · [简体中文](quality-gates.md)

`strategy_pipeline.pipeline.quality` provides shared run-quality gates. It normalizes `none`, `info`, `warning`, and `error` thresholds, recalculates a verdict from quality-check results, reads `summary.json` from a run directory, and checks whether release-protocol reports allow handoff.

```python
from strategy_pipeline.pipeline.quality import enforce_liveops_quality_gate

enforce_liveops_quality_gate(
    command_name="export-targets",
    run_dir=run_dir,
    config_ref=config_path,
    fail_on_quality="warning",
)
```

The caller or owner package produces the quality checks. The shared pipeline evaluates and enforces them; it does not calculate strategy metrics or access data providers. Public YAML parsing is used for configuration references. Credentials, private configuration, and research-specific rules stay in the caller's repository.
