# 按决策时点读取研究输入

`portfolio_backtester.point_in_time.PointInTimeDataView` 为每次策略决策绑定一个 `research.clock.v1`。读取时仅返回在 `information_cutoff_at` 之前已发布的记录。行情等需要限制事件日期的数据，还要声明 `event_at_col`。两个时间列都必须带时区，未知时间会拒绝加载。

```python
from portfolio_backtester.point_in_time import PointInTimeDataView, PointInTimeTable

view = PointInTimeDataView({
    "financials": PointInTimeTable(financials, available_at_col="published_at"),
    "daily_bars": PointInTimeTable(
        bars, available_at_col="available_at", event_at_col="session_close_at"
    ),
})

for decision_clock in decision_clocks:
    visible_financials = view.at(decision_clock).read("financials")
    visible_bars = view.at(decision_clock).read("daily_bars")
    targets = strategy(visible_financials, visible_bars)
```

上游必须提供真实的可用时间，不能用交易日期或财报期末日期代替发布时间。每个调仓决策分别绑定时钟。跨年任务的单个 Job 时钟不能代替逐次决策时钟。生成的目标仍需记录输入摘要与决策时钟，经过公共执行模拟和正式结果包校验后才能作为执行证据。该视图只约束通过它读取的数据，不验证策略代码是否还从其他路径读取了完整数据集。
