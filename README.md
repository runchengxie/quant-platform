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

This repository is licensed under the Apache License 2.0. See
[LICENSE](LICENSE). The license applies only to the original public framework
contents in this repository; it does not grant rights to private strategies,
proprietary data, credentials, or third-party dependencies.

The alpha framework's native implementation is `NativeDatasetBackend`.
The Qlib backend is connected through an optional dependency.

Public reusable quant research and portfolio platform. This repository is the
first published migration slice of the planned platform monorepo; it is not
yet a complete replacement for every legacy workspace submodule.

The current release migrates one public vertical slice from `portfolio-backtester`: the standalone
`portfolio_backtester.style_factors_backtest` quantile-portfolio kernel, a deterministic synthetic
CSV example, the `portfolio-style-factor` CLI, and the versioned
`portfolio_backtester.style_factor_backtest.v1` JSON artifact contract. It deliberately excludes
data providers, alpha generation, real strategy inputs, strategy-specific orchestration, and
execution runtime.

It also provides generic publication helpers under the owned `quant_platform` namespace and the
versioned `research-contracts` package under `packages/research-contracts/`. These packages own
manifest formatting, artifact envelopes, relative-path validation, SHA-256 receipts, and clean
bundle publication. They must not contain strategy-specific selection logic or proprietary
research inputs. The inherited contract package keeps its existing standalone quality gate while
the public prototype CI scopes Ruff to the migrated platform slice.

The source checkout at commit `91a4fa4f1d57c074c991546c381a3d90a3b6adfb` remains the rollback source
for the migrated portfolio slice. The Python namespace is unchanged. The
Apache-2.0 license applies to this repository's original public framework
contents only; it does not relicense the legacy source checkout or any
third-party dependency.

The remaining platform migration—data interfaces, alpha mechanisms,
microstructure abstractions, orchestration, and execution interfaces—must be
completed and audited before `research-workspace` switches its authoritative
sources.

详细迁移矩阵见 [`docs/migration/research-workspace-sunset.md`](docs/migration/research-workspace-sunset.md)。

Run locally:

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
