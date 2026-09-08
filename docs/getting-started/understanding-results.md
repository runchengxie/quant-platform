# 读取回测结果

`run_backtest` 的默认结果是一个五元素元组：

```python
stats, net_returns, gross_returns, turnover, periods = result
```

## 汇总统计

`stats` 通常包含总收益、年化收益、年化波动、Sharpe、最大回撤和平均换手率等指标。具体字段以当前代码和测试为准，常见读取方式如下：

```python
summary = {
    "total_return": stats["total_return"],
    "annualized_return": stats["ann_return"],
    "annualized_volatility": stats["ann_vol"],
    "sharpe": stats["sharpe"],
    "max_drawdown": stats["max_drawdown"],
}
```

如果某个指标没有足够的数据计算，结果可能是 `None` 或 `NaN`。读取结果时，应先确认样本长度和指标定义，再比较不同实验。

## 净收益和毛收益

- `gross_returns` 只反映持仓路径带来的收益。
- `net_returns` 在相同持仓路径上扣除了模型中的交易成本和滑点。
- 两者的差异可以帮助判断收益是否被换手和执行假设显著侵蚀。

示例：

```python
cost_drag = gross_returns - net_returns
```

这里的成本拖累是模型结果，不代表真实成交回报。真实成交需要订单、成交和账户账本等执行证据。

## 持有期明细

`periods` 是按持有期组织的字典列表。常见字段包括：

| 字段 | 含义 |
| --- | --- |
| `entry_date` | 持有期开始日期 |
| `exit_date` | 持有期结束日期 |
| `net_return` | 该持有期净收益 |
| `gross_return` | 该持有期毛收益 |
| `turnover` | 该持有期换手率 |
| `positions` | 该持有期使用的目标持仓 |

不同后端或配置可能附加更多字段。需要完整输出契约时，继续阅读[回测输出契约](../reference/outputs/backtest-outputs.md)和[持仓输出约定](../reference/outputs/positions.md)。

## 阅读结果时先问三个问题

1. 收益来自持仓路径，还是来自成本和价格假设的遗漏？
2. 回测使用的信号、价格和可交易性信息在当时是否已经可用？
3. 当前结果属于诊断性研究，还是具备完整执行证据的结果？

回测指标本身不能回答这些问题。需要结合输入数据、配置、持仓产物和执行证据一起检查。
