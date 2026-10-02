# 回测结果解读

语言：简体中文 · [English](backtest-interpretation.en.md)

本页说明组合回测侧的结果如何解读。预测质量、IC、CPCV、PBO 和特征重要度的解读见
`quant-market-research` 的结果解读文档。通用运行摘要和产物生命周期见
[输出摘要](../orchestration/output-summary.md)，跨项目字段约定见[公开 API 与产物契约](../reference/public-api.md)。

## 净收益与毛收益

相关文件：

- `backtest_net.csv`
- `backtest_gross.csv`

优先看净收益。毛收益适合观察未扣成本前的信号表现。净收益反映交易成本和滑点之后还能留下多少。

## 核心统计

`summary.json -> backtest.stats` 常见字段：

- `periods`
- `total_return`
- `ann_return`
- `ann_vol`
- `sharpe`
- `max_drawdown`
- `avg_holding`
- `periods_per_year`
- `avg_turnover`
- `avg_cost_drag`

怎么看：

- `periods`：参与统计的回测周期数。
- `total_return`：整个回测区间累计收益。
- `ann_return`：年化收益。
- `ann_vol`：年化波动。
- `sharpe`：单位风险对应的收益。
- `max_drawdown`：最大回撤。
- `avg_holding`：平均持有时间，通常近似为交易日数。
- `periods_per_year`：年化换算用的周期数。
- `avg_turnover`：每次调仓平均换手。
- `avg_cost_drag`：每期平均模拟成本。该字段按小数比例保存，例如 `0.001` 表示 0.1%。部分报告会转换为百分数显示。

## 风险指标

额外风险字段：

- `sortino`
- `calmar`
- `drawdown_duration`
- `recovery_time`
- `drawdown_duration_days`
- `recovery_time_days`
- `skew`
- `kurtosis`
- `var_95`
- `cvar_95`

怎么看：

- `sortino`：比 `sharpe` 更关注亏损波动。
- `calmar`：收益相对最大回撤是否划算。
- `drawdown_duration` / `drawdown_duration_days`：从前高跌到低点的周期数或自然日数。
- `recovery_time` / `recovery_time_days`：从低点回到前高的周期数或自然日数。
- `skew`：收益分布偏度。明显为负时，要警惕突发大亏。
- `kurtosis`：收益分布峰度。越高说明极端波动更常见。
- `var_95`：单期收益分布的第 5 百分位数。
- `cvar_95`：收益小于或等于 `var_95` 的观测值均值。这两个数描述历史样本，不代表未来损失上限。

## Benchmark 与主动收益

配置 `benchmark_symbol` 或 `benchmark_returns_file` 后，系统会输出：

- `summary.json -> backtest.benchmark`
- `summary.json -> backtest.active`
- `backtest_benchmark.csv`
- `backtest_active.csv`

主动收益常看字段：

- `tracking_error`
- `information_ratio`
- `beta`
- `alpha`
- `corr`
- `active_total_return`

怎么看：

- `tracking_error`：策略收益和基准收益的偏离波动。
- `information_ratio`：主动收益相对主动风险是否划算。
- `beta`：策略收益与基准收益协方差相对基准收益方差的比值。
- `alpha`：按拟合 beta 调整后的年化估计值。
- `corr`：策略收益和基准收益的相关性。
- `active_total_return`：策略累计收益相对基准累计收益的复利差值。

这些指标使用策略与基准都有数据的配对观测。比较回测前应核对基准定义和覆盖范围。

## 风格与行业暴露

如果回测包含持仓，且输入面板有可解析的暴露列，系统可能写出风格与行业暴露文件。这些文件描述组合暴露，不表示系统执行了中性化。`exposure-screen` 用于单独检查特定维度的集中情况。

## 滚动 Sharpe

`summary.json -> backtest.rolling_sharpe` 记录滚动 Sharpe 摘要和序列文件路径，窗口设置位于 `windows_months`。它展示不同历史窗口的变化，不代表独立样本或未来稳定性保证。滚动研究统计的实现在 `alpha_research.recency_diagnostics`。

## 常见误读

- 分桶 IC、暴露分析和容量压力测试回答不同问题，应分开解读。
- 预测侧的 `hit_rate` 不能替代回测收益、风险、成本和基准分析。
- 指标本身不能验证数据质量、点时可得性或执行假设。这些输入需要单独核对。
