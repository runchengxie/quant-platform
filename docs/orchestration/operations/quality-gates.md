# 质量闸门

`strategy_pipeline.pipeline.quality` 提供通用的运行质量闸门能力。

它负责：

- 规范化 `none`、`info`、`warning` 和 `error` 阈值
- 根据质量检查结果重新计算闸门状态
- 读取运行目录中的 `summary.json`
- 检查 release protocol 报告是否允许交接

模块不计算策略指标，也不读取数据 provider。质量检查结果由调用方或 owner 包生成，公共 pipeline 只负责统一判断和阻断交接。

```python
from strategy_pipeline.pipeline.quality import enforce_liveops_quality_gate

enforce_liveops_quality_gate(
    command_name="export-targets",
    run_dir=run_dir,
    config_ref=config_path,
    fail_on_quality="warning",
)
```

配置文件引用使用公开的 YAML 解析方式。凭证、私有配置和具体研究规则应留在调用方仓库。
