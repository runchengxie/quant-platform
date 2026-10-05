# quant-platform documentation

Language: English · [简体中文](README.zh-CN.md)

Translation coverage and the remaining page queue are tracked in the [localization status](LANGUAGE_MIGRATION_STATUS.md).

This documentation describes reusable quantitative research and portfolio mechanisms maintained by `quant-platform`. It is organized around current inputs, execution assumptions, output contracts, and development checks.

## Start here

1. [Platform overview](concepts/platform-overview.md)
2. [Installation and environments](getting-started/installation.md)
3. [Run your first backtest](getting-started/first-backtest.md)
4. [Understand backtest results](getting-started/understanding-results.md)
5. [Glossary](reference/glossary.md)

These guides use synthetic data and small examples. They help you run the full flow before exploring detailed interfaces and contracts.

## Further reading

1. [Repository README](https://github.com/runchengxie/quant-platform/blob/main/README.md)
2. [Common entry points](guides/entry-points.md)
3. [Multi-sleeve portfolio construction](guides/sleeve-portfolio.en.md)
4. [Incumbent requalification](guides/incumbent-requalification.en.md)
5. [Incumbent requalification OOS bridge](guides/incumbent-requalification-oos-controls.en.md)
6. [Promotion-evidence execution sidecar](guides/promotion-sidecar.en.md)
7. [Next-close diagnostic replay](guides/diagnostic-close-replay.en.md)
8. [Differential backtesting](concepts/differential-backtesting.en.md)
9. [Portfolio optimization backends](concepts/portfolio-optimization-backends.en.md)
10. [Composable backtest specification](concepts/backtest-spec.md)
11. [Backtest configuration parsing](concepts/backtest-configuration.md)
12. [Backtest backend boundary](concepts/backend-architecture.en.md)
13. [Costs and execution assumptions](concepts/execution-costs.md) · [Dated execution fees](dated-execution-fees.md)
14. [Execution capacity and daily NAV simulation](guides/execution-simulation.en.md)
15. [Turnover definitions](concepts/turnover.en-US.md)
16. [Cost breakdown](concepts/cost-breakdown.md)
17. [Factor return and risk attribution](concepts/factor-attribution.en.md)
18. [Raw-share corporate-action ledger](corporate-action-ledger.en.md)
19. [Interpreting backtest results](concepts/backtest-interpretation.en.md)
20. [Market benchmark comparisons](concepts/benchmark-ladder.en-US.md)
21. [Position output contract](reference/outputs/positions.md)
22. [Backtest output contract](reference/outputs/backtest-outputs.en.md)
23. [Execution allocation reference assets](reference/allocation-reference.md)
24. [Public API](reference/public-api.md)
25. [Testing and quality checks](testing.md) · [简体中文](testing.zh-CN.md)
26. [Execution domain](execution/README.en.md)
27. [Microstructure framework](microstructure/README.en.md) · [TickNet data boundary](microstructure/data-boundary.en.md)
28. [Microstructure development guide](microstructure/development-guide.en.md) · [Optional Rust kernel](development/microstructure-rust.en.md)

The [localization status](LANGUAGE_MIGRATION_STATUS.md) identifies pages that are still Chinese originals. They remain available in Chinese and are not linked here as English guides until their English versions are checked against the implementation.

Agents should start with the root README, this page, and the relevant category directory. They do not need to recursively read every Markdown file.

## Sources of truth

| Area | Implementation |
| --- | --- |
| Public package entry points | `packages/portfolio-backtester/src/portfolio_backtester/__init__.py` |
| Multi-sleeve portfolio construction | `packages/portfolio-backtester/src/portfolio_backtester/sleeve_portfolio.py` |
| Backtest specification | `packages/portfolio-backtester/src/portfolio_backtester/backtest_spec.py` |
| Backtest configuration parsing | `packages/portfolio-backtester/src/portfolio_backtester/backtest_config.py` |
| High-level API | `packages/portfolio-backtester/src/portfolio_backtester/api.py` |
| Input and output contracts | `packages/portfolio-backtester/src/portfolio_backtester/contracts.py` |
| Execution-domain contracts | `packages/portfolio-backtester/src/portfolio_backtester/execution_contracts.py` |
| Execution allocation reference | `packages/portfolio-backtester/src/portfolio_backtester/allocation_reference.py` |
| Backend protocols and normalized results | `packages/portfolio-backtester/src/portfolio_backtester/backends/` |
| Costs and slippage | `packages/portfolio-backtester/src/portfolio_backtester/execution.py` |
| Position replay | `packages/portfolio-backtester/src/portfolio_backtester/position_backtest.py` |
| Promotion-evidence execution simulation | `packages/portfolio-backtester/src/portfolio_backtester/promotion_sidecar.py` |
| Test entry point | `scripts/dev/run_tests.sh` |
| [Grid backtest helpers](grid-support.en.md) | `packages/portfolio-backtester/src/portfolio_backtester/grid_support.py` |
| Microstructure simulation API | `packages/microstructure/src/ticknet/simulator/` |
| Rust simulation kernel | `packages/microstructure/rust/src/lib.rs` |

When code, tests, and documentation disagree, verify the current implementation and correct the documentation in the same change.

## Project boundary

This repository documents general portfolio construction and backtesting behavior. Data downloads, factor research, model training, strategy-specific rules, job orchestration, and broker order placement belong to callers or other projects.

Historical migration records remain in pull requests, release notes, or maintenance records. User guides describe current inputs, behavior, and outputs.

## Historical ownership

- [Backtesting namespace](namespace-migration.md)
- [DailyWatch20 portfolio ownership](ownership-migration.md)
- [Incumbent requalification out-of-sample comparison bridge](guides/incumbent-requalification-oos-controls.md)

## Historical migration material

The read-only source copies under [`migration/legacy-materials/`](migration/legacy-materials/) preserve former repository layouts for comparison. They are not current APIs or supported development entry points. Start with the current ownership and migration pages above; consult a legacy copy only when reproducing a historical implementation or checking migration parity. The cross-repository historical index and file-level inventory are maintained in the private [`quant-research` migration index](https://github.com/runchengxie/quant-research/blob/main/docs/migration/HISTORICAL-RESEARCH-INDEX.md).
