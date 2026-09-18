# 评估编排

`strategy_pipeline.pipeline.eval` 负责把一次评估窗口中的指标计算、组合回放和结果产物连接起来。

它把评分指标交给 `alpha-research`，把持仓、净值、换手和暴露产物交给 `portfolio-backtester`。模块自身只负责统一输入、调用顺序和结果字典结构，不包含具体策略规则。

## 公开入口

```python
from strategy_pipeline.pipeline.eval import (
    _build_period_positions,
    _evaluate_period,
)
```

这些以下划线开头的函数主要供公共 pipeline 的 owner hook 使用。策略仓库应通过 `strategy_pipeline.control_plane` 的公开协议接入，避免直接依赖内部结果字段。

## 空评估窗口

没有测试数据时，`_evaluate_period` 返回结构完整的空结果。调用方可以继续生成统一的 run 摘要，不需要为缺失评估窗口创建另一套分支。
