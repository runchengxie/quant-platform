# research-workspace sunset 与 quant-platform 边界

> status: active
> owner: quant-platform
> audience: human and agent
> last_verified: 2026-09-06

## 目标

`quant-platform` 是通用量化平台能力的权威仓库。`research-workspace` 和旧 platform submodule 进入迁移兼容期，不再作为新公共能力的默认实现位置。

## 放置规则

| 内容 | 归属 |
| --- | --- |
| 数据接入、标准化、质量治理、版本和 published asset | 独立的 `market-data-platform` |
| 通用数据消费 contract、回测、组合、风险和执行模拟 | `quant-platform` |
| 通用回测、组合构造、风险、成本、容量和执行模拟 | `quant-platform` |
| 现金流策略的专有规则、ML 特征和模型 | `quant-research` |
| 策略研究假设、实验和晋升证据 | `quant-research` |
| 报告、看板、Feishu 和运营交付 | `market-intel` |

平台通过 `market-data-platform` 发布的资产、公开 API、版本化 schema 和 artifact contract 与研究层连接，不导入研究仓或数据平台的内部 Python 模块。

## 兼容期规则

- 新平台能力不得只修改旧 `portfolio-backtester` 或旧工作区实现。
- 从旧仓迁移时先保留行为和 contract，再单独进行语义改造。
- 平台文档应说明可复用机制，不写入具体策略参数或私有结果。
- Apache-2.0 只覆盖本仓库明确属于公共框架的内容，不覆盖私有策略、数据、凭证和第三方依赖。
