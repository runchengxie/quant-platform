# Research workspace migration boundary

Language: English · [简体中文](research-workspace-sunset.md)

`quant-platform` is the authoritative repository for reusable portfolio and backtesting capabilities. The public framework migration is complete. The former `research-workspace` and the old platform submodule remain historical sources for compatibility checks, not active implementation targets.

## Where work belongs

| Work | Owner |
| --- | --- |
| Data ingestion, normalization, quality controls, versions, and published data assets | `quant-market-data-platform` |
| Reusable data-consumption contracts, backtesting, portfolios, risk, and execution simulation | `quant-platform` |
| Proprietary cash-flow rules, ML features, and models | `quant-research` |
| Strategy hypotheses, experiments, and promotion evidence | `quant-research` |
| Reports, dashboards, Feishu delivery, and operations | `quant-intel-platform` and `quant-intel-deploy` |

Projects connect through published data assets, public APIs, versioned schemas, and artifact contracts. `quant-platform` does not import internal Python modules from the research or data-platform repositories.

Since 2026-09-30, the platform distribution no longer packages a compatibility copy of `market_data_platform`; the old import path is unsupported. The data platform owns data-production capabilities and their contracts. `quant-platform` retains only the input normalization needed by its own portfolio and orchestration interfaces.

## Migration and licensing rules

- New platform behavior must not be implemented only in the old `portfolio-backtester` or former workspace.
- When migrating behavior, preserve the existing behavior and contract first; handle semantic changes separately.
- Public platform docs describe reusable mechanisms, not private strategy parameters or results.
- Apache-2.0 applies only to content in this repository that is explicitly part of the public framework. It does not grant rights to private strategies, data, credentials, or third-party dependencies.
