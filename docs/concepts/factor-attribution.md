# 因子收益和风险归因

语言：简体中文 · [English](factor-attribution.en.md)

`portfolio_backtester.factor_attribution` 提供两个计算函数：`attribute_factor_return()` 分解主动收益，`attribute_factor_risk()` 分解主动方差。两者都使用调用方提供的权重、暴露和因子输入，不负责估计这些输入。

## 收益归因

设 `w` 为组合权重，`b` 为基准权重，`X` 为资产因子暴露，`f` 为因子收益：

```text
active_weights       = w - b
active_exposures     = X' active_weights
factor_contributions = active_exposures * f
active_return        = portfolio_return - benchmark_return
cost_contribution    = -transaction_cost
specific_return      = active_return - sum(factor_contributions) - cost_contribution
```

`portfolio_return` 应为扣除交易成本后的组合收益，`benchmark_return` 应覆盖相同期间。`transaction_cost` 以非负收益数值传入，例如 5 个基点写作 `0.0005`。函数不会把基点换算为收益，也不会计算收益或成本。
特异收益是一个剩余项，使因子贡献和单独列出的成本拖累之和与传入的净主动收益一致。

`factor_return_attribution.v1` 回执包含主动暴露、因子贡献、特异收益、成本贡献、主动收益和核对后的主动收益。各项相加等于传入的主动收益。

## 风险归因

设 `F` 为因子收益协方差矩阵，`s` 为各资产的特异风险：

```text
factor variance contribution_i = e_i * (F e)_i
specific variance              = sum((active_weight_j * s_j)^2)
active variance                = sum(factor contribution) + specific variance
```

`F` 必须对称且为半正定矩阵。该计算假设不同资产的特异收益相互独立。因子协方差和特异风险应使用兼容的期间与单位。

`factor_risk_attribution.v1` 回执提供各因子方差贡献、特异方差贡献、主动暴露和主动方差。结果是方差，不是年化风险。

## 输入和范围限制

组合权重、基准权重和暴露矩阵必须包含完全相同的资产。因子收益以及协方差矩阵的行列必须与暴露矩阵的因子列完全匹配。所有数值必须有限，特异风险不能为负。标签不匹配时函数会报错，不会静默对齐或补齐缺失资产和因子。

这些函数不会估计因子暴露、因子收益、协方差或特异风险，也不计算 Brinson 配置或选股归因。输出只是对给定模型输入的算术分解，不能单独证明组合表现的因果来源。
