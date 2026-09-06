# 运行摘要

`strategy_pipeline.pipeline.output_summary_sections` 负责把一次研究运行的上下文和产物引用整理成结构化摘要。

它只处理通用的结果编排，包括运行信息、数据范围、数据集、信号产物、评估结果、组合回放、持仓、质量检查和 walk-forward 结果。策略逻辑、特征定义、数据 provider、凭证和执行策略由 owner 仓库提供。

## 使用方式

```python
from strategy_pipeline.pipeline.output_summary_sections import build_run_summary_sections

summary = build_run_summary_sections(context=context, artifacts=artifacts)
```

`context` 和 `artifacts` 是运行器提供的映射对象。该函数返回可序列化的分区字典，调用方可以继续写入 JSON 或运行报告。

函数依赖 `portfolio-backtester` 提供的执行模型和模拟配置描述接口，避免在公共 pipeline 中复制组合或执行领域实现。
