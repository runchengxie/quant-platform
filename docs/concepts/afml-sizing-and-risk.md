# AFML 仓位、HRP 与策略风险

语言：简体中文 · [English](afml-sizing-and-risk.en.md)

本页说明 `portfolio_backtester` 已实现的组合仓位、active-bet 聚合、层次风险平价（HRP）和策略风险工具。

## 校准仓位

`portfolio_backtester.bet_sizing` 根据研究层提供的输入构造非负、按 gross exposure 归一化的目标权重。支持的方法包括 `probability`、`probability_vol_target`、`signal_vol_target`、`confidence_budget` 和 `risk_budget`。还可设置 gross target、单标的上限、权重步长和最小交易权重。

调用方提供 `calibrated_probability`。波动率目标方法还需要 `predicted_volatility`，也可以指定其他列名。该函数不会训练模型或拟合校准器。概率校准及其样本外证据属于研究层。仓位约束只作用于组合权重，不能证明输入具有预测能力，也不能证明组合适合实盘。

```python
from portfolio_backtester import SizingConfig, build_sized_weights

weights = build_sized_weights(
    candidates,
    score_col="signal_backtest",
    config=SizingConfig(
        method="probability_vol_target",
        single_name_cap=0.05,
        step_size=0.005,
        min_trade_weight=0.005,
    ),
)
```

## Active bets

`average_active_bets` 会在每个时间点，对 `label_start` 至 `label_end` 范围内事件的 `bet_size` 求平均。

`discretize_weights` 将权重四舍五入到给定步长。它与 active-bet 聚合是独立操作。单独离散化不会执行组合限额或换手约束。

## HRP

`hierarchical_risk_parity` 根据收益 DataFrame 估计 HRP 权重。`rolling_hrp_weights` 在每个调仓日只使用该日之前、且受 lookback 限制的历史数据。HRP 需要 SciPy 和至少两个可用的收益序列。协方差中存在缺失值时会报错。

这些函数可用于资产、模型或 sleeve 收益序列，但不会替你决定应当组合哪些序列。对每日变化的 Top-K 股票池使用 HRP 并不意味着结果稳定。依赖结果前应检查聚类与权重稳定性、换手和样本外表现。

## 策略风险

`portfolio_backtester.strategy_risk` 提供概率夏普比率、正负收益集中度、命中率及平均盈亏、隐含精度、策略失效概率，以及实现差额和成本韧性指标。返回字段以 `StrategyRiskReport` 和各指标字典的定义为准。

`strategy_failure_probability` 根据观测到的盈亏分布和年交易频率假设，估计未来精度低于目标 Sharpe 所需精度的 bootstrap 概率。它是研究诊断指标，不能替代账户或组合 VaR。

## 产物

`portfolio_backtester.afml_evidence.generate_run_afml_evidence` 从已保存的运行目录读取数据并生成 sizing 和策略风险证据。配置 HRP 收益输入后，也会生成 HRP 证据。产物包括：

```python
from portfolio_backtester.afml_evidence import generate_run_afml_evidence

generate_run_afml_evidence("artifacts/runs/example")
```

```text
sizing_receipt.json
strategy_risk_report.json
hrp_receipt.json
hrp_weights.csv
```

HRP 收益输入是可选项，因此 HRP 文件也仅在提供该输入时生成。编排层可以把证据路径和哈希写入 lineage sidecar。这些报告不是下单指令。执行仍使用标准 `targets.json` 契约。
