# 运行产物

`strategy_pipeline.pipeline.output_artifacts` 负责把一次运行产生的数据集、特征、信号、评估结果、回测结果和诊断结果写入运行目录，并返回统一的产物路径清单。

模块只负责文件格式、路径和产物清单。数据 provider、信号计算、组合规则和执行模型由 owner 包提供。回测契约和持仓输出分别使用 `portfolio-backtester` 的公共接口，信号产物契约使用 `quant-market-research` 的公共接口。

```python
from strategy_pipeline.pipeline.output_artifacts import write_run_artifacts

artifacts = write_run_artifacts(context=context)
```

调用方需要提供运行上下文，并由配置决定是否写入具体产物。函数不会读取凭证，也不会生成策略信号或修改组合逻辑。

周度组合的历史净值由策略或回测 owner 生成。调用方如显式提供
`weekly_basket_performance_path`，pipeline 只把该路径登记到产物清单，不读取文件、
扫描运行目录、计算净值或导入策略代码。未提供时，该字段为 `None`。
