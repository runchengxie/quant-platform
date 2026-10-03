# 多次决策的统一执行回放

语言：简体中文 · [English](sequenced-execution.en.md)

`SequencedExecutionBackend` 接收每次调仓的目标权重、逐日价格和各自的 `research.clock.v1`，调用公共执行模拟器，返回 `CanonicalBacktestResult`、订单、成交和每日账本。每个 `rebalance_date` 必须有一个独立时钟，`entry_date` 必须处于该时钟的执行窗口内。启用涨跌停或上市状态约束时，相应的每日输入列必须完整。

```python
from portfolio_backtester.backends import SequencedExecutionBackend, SequencedExecutionRequest
from portfolio_backtester.execution_sim import ExecutionSimConfig

result = SequencedExecutionBackend().run(
    SequencedExecutionRequest(
        positions=targets,  # rebalance_date, entry_date, symbol, weight
        pricing=daily_prices,  # trade_date, symbol, close, amount, tradable, ...
        decision_clocks=clocks,  # {rebalance_date: research.clock.v1}
        config=ExecutionSimConfig(enabled=True, liquidity_cols=("amount",)),
        tradable_col="tradable",
    )
)
```

本接口只验证已提交的目标、日期与市场规则数据。调用方仍须证明每次生成目标时所读数据的真实可用时间，并保存源文件摘要。`PointInTimeDataView` 可以约束具备可用时间戳的输入。没有逐次决策输入可见性证明时，结果只能作为执行模拟诊断，不得标为正式时点合规回测。现有 `write_execution_aware_result_bundle` 只接受单一时钟，会拒绝多次决策结果。原始价格的除权分红需要提供明确的 `CorporateAction` 事件。只提供复权因子时应标记为价格代理实验。
