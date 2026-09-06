# quant-platform

策略假设、专有特征和晋升证据属于私有研究层。本仓库只提供可复用的研究、回测和产物接口。

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
