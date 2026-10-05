# Alpha and research documentation

Language: English · [简体中文](README.zh-CN.md)

This section documents reusable alpha-research interfaces and model-related methods. Project-specific hypotheses, proprietary features, and promotion decisions belong in the owning research project.

## Start here

| Topic | Documentation |
| --- | --- |
| Project scope and installation | [Repository README](https://github.com/runchengxie/quant-platform/blob/main/README.md) |
| Model selection | [English canonical](concepts/model-selection.en-US.md) · [Chinese companion](concepts/model-selection.md) |
| Model landscape | [English canonical](concepts/model-landscape.en-US.md) · [Chinese companion](concepts/model-landscape.md) |
| Factor catalog | [English canonical](concepts/factor-catalog.en-US.md) · [Chinese companion](concepts/factor-catalog.md) |
| Factor risk model | [English canonical](concepts/factor-risk-model.en-US.md) · [Chinese companion](concepts/factor-risk-model.md) |
| Signal drift | [English canonical](concepts/signal-drift.en-US.md) · [Chinese companion](concepts/signal-drift.md) |
| Factor-expression DSL | [English canonical](concepts/factor-expression.en-US.md) · [Chinese companion](concepts/factor-expression.md) |
| Overfitting controls | [English canonical](concepts/overfitting-controls.en-US.md) · [Chinese companion](concepts/overfitting-controls.md) |
| Research protocols | [English canonical](concepts/research-protocols.en-US.md) · [Chinese companion](concepts/research-protocols.md) |
| Feature research | [English canonical](concepts/feature-research-protocol.en-US.md) · [Chinese companion](concepts/feature-research-protocol.md) |
| StyleReplica | [English canonical](concepts/style-replica.en.md) · [Chinese companion](concepts/style-replica.md) |
| Signal artifact contract | [English canonical](reference/signal-artifacts.en-US.md) · [Chinese companion](reference/signal-artifacts.md) |
| Research output contract | [English canonical](reference/research-outputs.en-US.md) · [Chinese companion](reference/research-outputs.md) |
| Other research concepts | [Fundamental-state forecasting](concepts/fundamental-state-forecasting.md), [formation-date cross-sections](concepts/style-factor-cross-sections.md), [contextual factors](concepts/contextual-factors.md), [AFML methods](concepts/afml-methodology.md), [research backends](concepts/framework-backends.md), and [minute-factor boundaries](concepts/minute-factors.md) (Chinese originals) |
| Research template | [Design guide](guides/research-template-design.md) (Chinese original) |
| Namespace migration | [Migration note](namespace-migration.md) (Chinese original) |
| Testing | [Research testing and quality checks](operations/testing.md) (Chinese original) |

## Ownership boundary

This repository documents reusable mechanisms such as feature-evidence interfaces, model evaluation methods, and signal-artifact contracts. General portfolio backtesting, trading costs, capacity analysis, orchestration, CLI behavior, configuration composition, run directories, and target-file export are maintained here; the Python namespaces remain `portfolio_backtester` and `strategy_pipeline`.

Keep strategy hypotheses, proprietary features, model-specific portfolio rules, and promotion decisions in the owning research project. When migrating a document, update the old page with a redirect or status note so readers do not encounter multiple active copies.
