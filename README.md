# quant-platform

`quant-platform` 是公开的量化研究与投资组合基础平台。

它提供可复用的回测、组合、执行模拟、风险分析和研究产物接口，供研究项目调用。策略假设、专有特征、真实策略输入和晋升证据属于 `quant-research` 等私有研究层，本仓库不保存这些内容。

## 适合谁使用

- 想运行示例回测的研究者
- 需要复用组合、风险或产物接口的开发者
- 需要了解公开量化基础能力边界的维护者

## 快速开始

安装开发依赖并运行检查：

本仓库按 Apache License 2.0 授权，详见 [LICENSE](LICENSE)。许可证只适用于本仓库中的公开框架代码，
不授予私有策略、专有数据、凭证或第三方依赖的使用权。

alpha 框架的原生实现是 `NativeDatasetBackend`。Qlib 后端通过可选依赖接入。

这是公开的可复用量化研究与组合平台。当前仓库仍处于分阶段迁移中，旧工作区的其他职责尚未全部迁入。

当前版本从 `portfolio-backtester` 迁入一组独立的公开能力，包括
`portfolio_backtester.style_factors_backtest` 分位数组合内核、确定性的合成 CSV 示例、
`portfolio-style-factor` 命令行入口，以及版本化的
`portfolio_backtester.style_factor_backtest.v1` JSON 产物契约。数据供应商、alpha 生成、真实策略输入、
策略专属编排和执行运行时仍不属于本仓库。

仓库还在自有的 `quant_platform` 命名空间下提供通用发布辅助工具，并提供
`packages/research-contracts/` 下的版本化 `research-contracts` 包。这些包负责清单格式化、
产物封装、相对路径校验、SHA-256 回执和干净的 bundle 发布，不应包含策略专属选股逻辑或私有研究输入。
继承而来的契约包保留独立质量门禁，公开 CI 只对已迁入的平台代码执行 Ruff 检查。

具体迁移来源提交为 `91a4fa4f1d57c074c991546c381a3d90a3b6adfb`，用于回滚核对。
Python 命名空间保持不变。Apache-2.0 许可证只适用于本仓库原有的公开框架代码，
不会改变旧来源代码或第三方依赖的许可证。

数据接口、alpha 机制、微观结构抽象、编排和执行接口仍在分阶段迁移与审计。
`research-workspace` 已进入 sunset 阶段，迁移完成前只用于历史核对和兼容验证。

Run locally:

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run pytest
```

运行一个公开示例：

```bash
uv run portfolio-style-factor \
  --input examples/synthetic-style-factor.csv \
  --output /tmp/style-factor-report.json \
  --signal size \
  --quantiles 2
```

## 去哪里找详细说明

- [文档总览](docs/README.md)
- [开发约定](AGENTS.md)
- [回测与组合说明](docs/concepts/backtest-spec.md)
- [研究产物与公开接口](docs/reference/public-api.md)
- [迁移与边界说明](docs/migration/research-workspace-sunset.md)

文档中的技术说明以当前代码和测试为准。README 只保留项目定位、使用入口和导航，具体接口、架构、兼容性和迁移记录请查看 `docs/`。

## 仓库边界

`quant-platform` 负责通用能力，例如回测、组合构造、风险和成本、执行模拟，以及可复用的研究产物契约。

以下内容由其他仓库负责：

- `market-data-platform`：数据采集、清洗、质量检查、版本和发布
- `quant-research`：策略、特征、机器学习、实验和研究结论
- `market-intel`：报告、看板和研究结果交付

研究项目通过已发布的数据资产和版本化产物与本仓库协作。`quant-platform` 不接入数据供应商，不保存真实策略输入，也不承载专有策略逻辑。

## 许可证

本仓库采用 Apache License 2.0。许可范围仅包括本仓库中的公开框架代码，不包含私有策略、专有数据、凭证和第三方依赖。

详见 [LICENSE](LICENSE)。
