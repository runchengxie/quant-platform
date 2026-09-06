# 因子目录

因子目录把可复用因子整理成带版本的研究资产，不再把身份隐含在 Python 函数名中。

每个 `FactorSpec` 记录：

- 稳定的因子 ID 和明确版本。
- owner 和频率。
- 已声明的依赖。
- PIT 语义。
- 形成股票池的语义。
- 预处理流程。
- 实现代码的 SHA-256。
- 可选说明。

`FactorEvidenceSummary` 记录带日期的证据，不嵌入原始研究输出。首批摘要字段包括 IC、rank IC、ICIR、换手率、
中性化 rank IC、衰减周期、观测数量和生命周期状态（`research`、`candidate`、`production`、`retired`）。

一个目录可以包含同一因子的多个版本。证据必须绑定到唯一的 `(factor_id, version)`，证据日期重复时直接关闭。

本设计参考 RQFactor 相关讨论中的因子生命周期和产品化思路，同时把 PIT 语义和证据归属保留在本平台。
未来可以使用 Alphalens Reloaded 提供差异化 tear sheet 检查，但它不会成为权威因子身份库。
