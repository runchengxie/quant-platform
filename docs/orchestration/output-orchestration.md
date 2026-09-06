# 运行输出编排

`strategy_pipeline.pipeline.output.persist_run_outputs` 负责协调一次运行的输出生命周期。
它依次写入运行产物、生成可选证据、构建摘要、写入元数据。

摘要、证据和元数据的具体内容由调用方通过回调提供。公共包只负责流程边界，不包含具体策略、
模型或研究结论。

```python
from strategy_pipeline.pipeline.output import persist_run_outputs

persist_run_outputs(
    context=context,
    evidence_builder=build_evidence,
    summary_builder=build_summary,
    metadata_writer=write_metadata,
)
```

所有回调都接收关键字参数。`evidence_builder` 可以向 `artifacts` 映射补充证据路径，随后摘要
构建器会看到更新后的内容。`SAVE_ARTIFACTS` 为假时，产物写入和所有回调都会跳过。
