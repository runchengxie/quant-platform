# Barra-like 风险模型内核

语言：简体中文 · [English](risk-model-kernel.md)

`portfolio_backtester.risk_model` 提供小型、公开且与策略无关的风险模型，用于研究诊断。它只是一个 Barra-like 内核，不代表兼容任何商业供应商的模型。

## 职责边界

调用方负责按点时原则（PIT）构造暴露和收益。内核不获取数据、不推断证券范围、不构建 A 股因子，也不执行指数编制方法。A 股因子构建器和报告适配器属于 `quant-market-research`。私有现金流、小微盘和 DailyWatch20 持仓属于 `quant-research`。

## 输入契约

暴露是一个宽表 `pandas.DataFrame`，索引为两层 `as_of_date` 和 `symbol`。其余列分别表示因子暴露。收益面板是索引相同的 `Series`，或列名为 `total_return` 的单列 `DataFrame`。重复键和非有限收益会被拒绝。缺失因子暴露不会被静默填补。缺少完整因子集合的行会从当日回归中排除，并出现在诊断结果里。

PIT 数据所有者应同时记录数据源版本、发布时间、资格规则、公司行动口径和因子定义版本。数值内核不会猜测这些元数据。

## 估计方法

`estimate_factor_returns` 对每个日期执行一次加权截面岭回归：

\[
r_{i,t} = X_{i,t} f_t + e_{i,t}.
\]

模型不自动添加截距项。需要截距时，应提供名为 `intercept` 的暴露列。结果包含因子收益、拟合收益与残差收益，以及逐日观测数、矩阵秩、条件数和加权 R² 诊断。

`build_risk_model` 使用历史因子收益估计指数加权因子协方差，将其向对角矩阵收缩，并把数值上为负的特征值投影为零。个股特质方差是按证券计算的指数加权残差方差。这些处理用于稳定统计计算，不构成经济保证。

给定组合权重 \(w\)、暴露矩阵 \(B\)、因子协方差 \(\Sigma\) 和对角特质方差 \(D\)：

\[
b = B^T w,\qquad
\sigma^2_{factor} = b^T\Sigma b,\qquad
\sigma^2_{specific} = \sum_i w_i^2 D_i.
\]

`attribute_portfolio_risk` 返回因子暴露、Euler 因子方差贡献 \(b_j(\Sigma b)_j\)、特质方差、总方差和波动率。按定义，各项贡献之和等于因子方差。

## 合成数据示例

```python
factor_result = estimate_factor_returns(exposures, returns)
risk = build_risk_model(
    factor_result.factor_returns,
    factor_result.residual_returns,
)
attribution = attribute_portfolio_risk(
    weights,
    exposures_for_model_date,
    risk.factor_covariance,
    risk.specific_variance,
)
```

解释结果前应先检查诊断信息。截面样本不足、矩阵条件较差、PIT 暴露缺失、残差历史过短或协方差特征值不稳定，都应作为证据限制明确说明。
