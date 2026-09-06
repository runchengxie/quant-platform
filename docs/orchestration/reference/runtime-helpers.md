# 运行时辅助能力

`strategy_pipeline.pipeline.runtime` 提供研究运行需要的通用辅助能力，包括日志配置、配置哈希、最终留出集长度换算、purge 和 embargo 步数换算，以及训练和测试日期切分。

日期切分和评估规则通过 `alpha-research` 的公共接口完成，rebalance 间隔通过 `portfolio-backtester` 的公共接口估算。模块不读取策略配置，也不访问凭证或数据 provider。

```python
from strategy_pipeline.pipeline.runtime import config_hash, setup_logging

run_hash = config_hash(config)
log_file = setup_logging(config, default_log_file=run_dir / "run.log")
```
