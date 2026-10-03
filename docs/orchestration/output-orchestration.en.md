# Run-output orchestration

Language: English · [简体中文](output-orchestration.md)

`strategy_pipeline.pipeline.output.persist_run_outputs` coordinates a run's output lifecycle. In order, it writes configured artifacts, invokes an optional evidence builder, builds a summary, and writes metadata.

```python
from strategy_pipeline.pipeline.output import persist_run_outputs

persist_run_outputs(
    context=context,
    evidence_builder=build_evidence,
    summary_builder=build_summary,
    metadata_writer=write_metadata,
)
```

The caller supplies the summary, evidence, and metadata behavior through callbacks. Each callback receives keyword arguments. The evidence builder may add paths to the `artifacts` mapping; the summary builder then receives that updated mapping.

If `context["SAVE_ARTIFACTS"]` is false or missing, no artifacts are written and no callbacks run; the function returns an empty mapping. Otherwise, the return value is the artifact mapping from `write_run_artifacts`.
