# 运行第一个回测

本页使用一份很小的合成数据，演示从分数、执行模型到回测结果的完整流程。示例中的价格和信号只用于学习 API，不代表任何投资观点。

## 1. 准备数据

回测输入是一张 `pandas.DataFrame`。最小示例需要以下列：

| 列 | 含义 |
| --- | --- |
| `trade_date` | 交易日期 |
| `symbol` | 证券标识 |
| `signal` | 用于排序和选股的分数 |
| `close` | 执行模型使用的价格 |

下面的四只证券有三个交易日，每天都会重新排名：

```python
import pandas as pd

scores = pd.DataFrame(
    {
        "trade_date": pd.to_datetime(
            ["2020-01-01"] * 4 + ["2020-01-02"] * 4 + ["2020-01-03"] * 4
        ),
        "symbol": ["A", "B", "C", "D"] * 3,
        "signal": [4.0, 3.0, 2.0, 1.0, 3.0, 4.0, 2.0, 1.0, 3.0, 4.0, 2.0, 1.0],
        "close": [
            100.0, 100.0, 100.0, 100.0,
            110.0, 90.0, 105.0, 100.0,
            121.0, 81.0, 110.25, 100.0,
        ],
    }
)
```

## 2. 配置执行模型

执行模型负责开仓价格、退出价格、成本和滑点。这个示例先关闭显式交易成本，让结果更容易理解：

```python
from portfolio_backtester.execution import build_execution_model

execution = build_execution_model(
    {"entry": {"price_col": "close"}, "exit": {"price_col": "close"}},
    default_cost_bps=0.0,
    default_exit_price_policy="strict",
    default_exit_fallback_policy="ffill",
    default_price_col="close",
)
```

## 3. 配置策略和回测

`StrategySpec` 描述如何选股和分配权重。`BacktestSpec` 把策略、执行模型和回测区间组合在一起：

```python
from portfolio_backtester import BacktestSpec, StrategySpec, run_backtest

spec = BacktestSpec(
    strategy=StrategySpec(
        name="topk-demo",
        type="topk_buffered_long_only",
        score_col="signal",
        top_k=2,
        weighting="equal",
    ),
    execution=execution,
    rebalance_dates=tuple(pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])),
    shift_days=0,
    trading_days_per_year=252,
)

result = run_backtest(scores, spec)
if result is None:
    raise RuntimeError("没有形成可回放的持仓")
```

## 4. 读取结果

默认返回值包含五部分：

```python
stats, net_returns, gross_returns, turnover, periods = result

print(stats["total_return"])
print(net_returns)
print(periods[0]["entry_date"], periods[0]["exit_date"])
```

其中：

- `stats` 是汇总统计字典
- `net_returns` 是扣除模型成本后的持有期收益
- `gross_returns` 是未扣成本的持有期收益
- `turnover` 是各持有期的换手率
- `periods` 保存每个持有期的日期、持仓和收益明细

完整字段说明见[读取回测结果](understanding-results.md)。需要成本、滑点或可交易性约束时，再阅读[成本与执行假设](../concepts/execution-costs.md)。

## 这个示例省略了什么

真实研究通常还需要：

- 使用已发布、带版本信息的数据资产
- 明确信号的形成时间和可用时间
- 检查价格、流动性和交易状态字段
- 设置成本、滑点和市场规则
- 保存配置、持仓、定价数据和运行产物

这个页面只负责帮助你理解调用关系。正式研究前，请阅读[组合式回测规范](../concepts/backtest-spec.md)和[回测结果解读](../concepts/backtest-interpretation.md)。
