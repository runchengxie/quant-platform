# Glossary

Language: English · [简体中文](glossary.zh-CN.md)

This page defines terms used throughout the documentation. Code, configuration, and API names retain their English spelling.

| Term | Definition |
| --- | --- |
| signal | A value used to rank or filter securities, or construct target positions. |
| target position | The securities and weights a strategy intends to hold after rebalancing. |
| sleeve | An independent strategy or configuration unit within a portfolio. |
| backtest | A replay of portfolio behavior from historical inputs under explicit execution assumptions. |
| execution | The rules describing how orders fill, including prices, costs, slippage, and trading constraints. |
| backend | A component that implements a backtesting or portfolio-computation method. |
| ledger | A record of account state by order, fill, position, cash, and net asset value. |
| artifact | A run output such as positions, returns, summaries, manifests, or evidence files. |
| bundle | A related set of files organized under an agreed directory structure and manifest. |
| sidecar | An evidence file stored alongside a primary result, for diagnostics, hashes, or promotion rationale. |
| owner | The project or module responsible for maintaining a domain, data asset, or interface. |
| pipeline | A workflow that coordinates configuration, execution, evaluation, and artifact handoff. |
| PIT | Point-in-time: aligning information to what was available at the time, avoiding future information. |
| OOS | Out-of-sample data or an out-of-sample evaluation period. |
| AFML | *Advances in Financial Machine Learning*. Here, it refers to related position-sizing, risk, and research methods. |
| HRP | Hierarchical Risk Parity, a portfolio-construction method. |

When a term first appears, read its inputs, outputs, and boundaries in context, then use this page for a short definition. Current code, tests, and public contracts determine the final semantics.
