# Documentation localization status

English is the canonical language for public documentation. Chinese companions use the `.zh-CN.md` suffix. Both pages are published at distinct URLs, and each translated page links directly to its counterpart so readers can share a locale-specific URL.

The MkDocs sidebar follows the current page language. English pages show the English navigation; Chinese companions and untranslated Chinese originals show the Chinese navigation. This changes navigation only: existing URLs are preserved, and site search can still return pages in either language. Chinese originals without a checked English counterpart remain available at their current URLs.

## Completed entry pages

The backtest backend boundary and portfolio sizing and strategy-risk evidence now have English canonical pages paired with Chinese companions.

The [dated execution-fee reference](dated-execution-fees.md) now has a linked Chinese companion. The page documents caller-supplied fee periods and the current continuous-ledger integration; it does not claim to provide market defaults or broker-invoice replication.

The former style-factor weighting guide described a slice excluded from the public release over unresolved source licensing. Its public API entries and current-use claims have been removed. The original URL now carries a bilingual retirement notice, with historical detail retained in Git history.

The repository README, documentation index, platform overview, installation guide, first-backtest tutorial, results guide, backtest result interpretation, glossary, language policy, common entry points, execution simulation guide, point-in-time research data guide, sequenced execution guide, incumbent requalification guide, incumbent requalification OOS bridge, promotion-evidence execution sidecar, multi-sleeve portfolio construction guide, next-close diagnostic replay, differential backtesting, portfolio optimization backends, public API reference, allocation reference, position output contract, backtest output contract, data boundary, backtest configuration reference, backtest specification, canonical backtest bundle, execution-cost assumptions, cost breakdown, raw-share corporate-action ledger, factor return and risk attribution, turnover definitions, market benchmark comparisons, testing and quality checks guide, orchestration overview, control-plane API, evaluation orchestration, run artifacts, owner integration, target export, output orchestration, run summary sections, evidence and protocol CLI, quality gates, runtime helpers, orchestration reference index, orchestration configuration reference, orchestration CLI-helper reference, model selection guide, model landscape, factor catalog, factor risk model, signal drift, factor-expression DSL, signal-artifact contract, execution-domain overview, microstructure overview, TickNet data boundary, microstructure development guide, and optional Rust kernel guide have English canonical pages and linked Chinese companions. Other orchestration and alpha/research guides remain Chinese originals pending translation. MkDocs uses English as its default interface language.

## Remaining work

Many active MkDocs pages are still Chinese-only. Untranslated pages remain grouped as Chinese originals while translation is in progress. Prioritize pages by reader impact:

1. Configuration, CLI, and data-contract references.
2. Backtest specifications, execution and cost assumptions, output contracts, and operational runbooks.
3. Alpha and research-concept pages that are part of the public product surface.
4. Historical migration records and archived plans, after active user-facing docs are complete.

Do not create an English page by translating stale prose alone. Verify each page against current code, configuration, CLI help, tests, and artifacts. Keep identifiers and machine-readable contracts unchanged. Update this tracker as paired pages are added, and ensure the Chinese companion remains consistent with the English source.
