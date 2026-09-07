# 因子目录

因子目录将可复用因子整理为有版本的研究资产，避免因子身份只隐含在 Python 函数名中。

每个 `FactorSpec` 记录：

- 稳定的因子标识和明确版本
- 所属方和频率
- 声明的依赖
- 点时语义
- 建仓股票池语义
- 预处理流程
- 实现 SHA-256
- 可选说明

`FactorEvidenceSummary` 记录带日期的证据，不嵌入原始研究输出。首批摘要字段包括 IC 或 rank IC、ICIR、换手率、中性化 rank IC、衰减周期、观测数量和生命周期状态（`research`、`candidate`、`production`、`retired`）。

一个目录可以包含同一因子的多个版本。证据必须关联到精确的 `(factor_id, version)`，同一日期出现重复证据时直接拒绝。

本设计参考了 RQFactor 讨论中的因子生命周期和产品化思路，同时将点时语义和证据归属保留在本平台内。后续可以使用 Alphalens Reloaded 做差异化 tear sheet 检查，但它不承担规范的因子身份存储职责。
