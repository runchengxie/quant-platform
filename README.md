# quant-platform

> 这是新的公共量化平台仓库。新建的通用数据、回测、组合、风险和执行模拟能力应进入这里，不再写回 `research-workspace` 或旧的 `portfolio-backtester` 等 submodule。

如果你第一次接触本项目，先看[迁移说明](docs/migration/research-workspace-sunset.md)，再按下面的新人路径阅读。

策略假设、专有特征和晋升证据属于私有研究层。本仓库只提供可复用的研究、回测和产物接口。

简单说，`quant-platform` 提供可以被多个策略复用的工具。`quant-research` 决定某条具体策略为什么这样做。平台不应知道某个策略的专有选股规则，也不应保存真实策略数据、凭证或部署秘密。

## 新人阅读路径

1. 先看本页，理解平台和研究仓的边界。
2. 再看 [`docs/README.md`](docs/README.md)，找到概念、指南、编排和测试说明。
3. 需要理解回测时先看 `docs/concepts/backtest-spec.md` 和 `docs/guides/entry-points.md`。
4. 需要理解组合权重时看 `docs/concepts/style-factor-portfolio-weighting.md` 和 `docs/guides/sleeve-portfolio.md`。

现金流策略本身属于 `quant-research`。现金流指数权重、基准相对 overlay、组合约束和 D11-H5 分批执行等可复用机制，经过抽象后可以进入本仓库。

本仓库采用 Apache License 2.0，详见 [LICENSE](LICENSE)。许可证只适用于本仓库中的原始公开框架内容，
不授予私有策略、专有数据、凭证或第三方依赖的使用权。

alpha 框架的原生实现是 `NativeDatasetBackend`。Qlib 后端通过可选依赖接入。

本仓库提供公开、可复用的量化研究和组合平台能力，是规划中平台 monorepo 首个已发布的迁移切片。
当前版本还没有完全替代旧工作区的所有子模块。

当前版本从 `portfolio-backtester` 迁移了一条公开垂直切片，包括独立的
`portfolio_backtester.style_factors_backtest` 分位数组合内核、确定性的合成 CSV 示例、
`portfolio-style-factor` CLI，以及带版本的 `portfolio_backtester.style_factor_backtest.v1` JSON 产物契约。
数据供应商、alpha 生成、真实策略输入、策略专用编排和执行运行时不属于本次迁移范围。

本仓库还在自有的 `quant_platform` 命名空间下提供通用发布辅助工具，并在
`packages/research-contracts/` 下提供带版本的 `research-contracts` 包。这些包负责清单格式化、
产物封装、相对路径校验、SHA-256 回执和整洁的产物包发布。它们不得包含策略专用选股逻辑或私有研究输入。
继承的契约包继续使用原有的独立质量门禁，公开原型 CI 只对已迁移的平台切片运行 Ruff 检查。

提交为 `91a4fa4f1d57c074c991546c381a3d90a3b6adfb` 的源代码 checkout 仍是已迁移组合切片的回滚来源。
Python 命名空间保持不变。Apache-2.0 许可证只适用于本仓库中的原始公开框架内容，不会重新授权旧源代码
checkout 或任何第三方依赖。

剩余的平台迁移包括数据接口、alpha 机制、微观结构抽象、任务编排和执行接口。
这些部分完成审计前，`research-workspace` 不会切换权威来源。

详细迁移矩阵见 [`docs/migration/research-workspace-sunset.md`](docs/migration/research-workspace-sunset.md)。

本地运行：

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run pytest
uv run portfolio-style-factor \
  --input examples/synthetic-style-factor.csv \
  --output /tmp/style-factor-report.json \
  --signal size \
  --quantiles 2
```
