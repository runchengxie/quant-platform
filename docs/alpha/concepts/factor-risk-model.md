# 因子风险模型边界

`alpha-research` 当前维护一个与框架无关的轻量因子风险基础能力，将已经计算好的因子收益历史和特异收益历史转换为受 PIT 约束的风险估计。

## 模型

For exposure matrix `X`, factor covariance `F`, and specific variance diagonal `D`, the projected asset covariance is:

```text
Sigma_asset = X F X' + D
```

首个实现不从股票收益估计因子收益。因子构造属于研究假设，由调用方明确提供。
本函数只校验并汇总研究层已经生成的历史数据。

## 输入

- 当前或 as-of 时点的资产 × 因子暴露。
- 历史因子收益。
- 历史资产特异收益。
- 明确的 `as_of` 时间戳。
- 向因子方差对角线收缩的协方差估计。
- 最少共同观测数量。

所有收益观测都必须不晚于 `as_of`。未来数据行会直接关闭。

## 输出

`FactorRiskModelEstimate` 包含：

- 因子协方差。
- 各资产特异风险。
- 资产暴露。
- 历史起止时间和观测数量。
- 估计器配置。
- `asset_covariance()` 投影。
- 带版本的回执元数据。

## 后续工作

- 评估行业和风格因子集合以及估计窗口。
- 增加估计器比较和稳定性诊断。
- 通过研究产物发布风险模型证据。
- 将权威估计接入 `portfolio-backtester` 优化请求。
- 获得授权数据后，与获得许可的 RQData 风险模型输出比较。

第三方风险模型对象必须保留在适配器内部。晋升证据必须区分估计器质量和优化器质量。
