# 因子收益和风险归因

本模块提供轻量的多因子归因基础能力，参考 RQPAttr 中适合复用的部分，同时明确平台风险模型、
基准语义和成本核算口径。

## 主动收益

For portfolio weights `w`, benchmark weights `b`, exposures `X`, and factor returns `f`:

```text
active_weights   = w - b
active_exposure  = X' active_weights
factor_return    = active_exposure * f
net_active       = factor_return + specific_return - transaction_cost
```

`attribute_factor_return()` 报告各因子贡献、剩余特异收益和交易成本拖累。各项组成会与传入的净主动收益核对一致。

## 主动风险

For factor covariance `F` and per-asset specific risk `s`:

```text
factor variance contribution_i = e_i * (F e)_i
specific variance              = sum((active_weight_j * s_j)^2)
active variance                = sum(factor contribution) + specific variance
```

这里假设特异收益相互独立。因子协方差和特异风险估计属于独立的研究输入，本模块不会自行生成。

## 边界

Brinson 配置和选股归因单独处理。多因子风险模型与 Brinson 行业配置回答的是不同问题，
不能混成含义不清的一套分解。

未来的 Dashboard 展示层可以直接展示平台结果中的因子、风格和行业贡献、特异贡献以及成本拖累，
无需在 React 中重新计算。
