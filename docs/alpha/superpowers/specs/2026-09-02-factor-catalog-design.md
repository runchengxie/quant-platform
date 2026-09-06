# 因子目录设计

## 目标

为可复用因子提供稳定的版本化身份和带日期的证据，让维护者无需阅读实现代码，就能检查依赖关系、PIT 语义、预处理、实现身份和生命周期。

## 设计

`FactorSpec` is immutable identity metadata. `FactorEvidenceSummary` is a small dated evidence record. `FactorCatalog` registers exact `(factor_id, version)` pairs, rejects duplicates, and serializes to a platform-owned schema.

原始因子值、模型对象、供应商对象和完整分析报告不进入目录。Alphalens 或 RQFactor 风格的分析结果经过标准化后可以作为证据输入，但它们都不维护因子身份。
