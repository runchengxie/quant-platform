# Documentation localization status

English is the canonical language for public documentation. Chinese companions use the `.zh-CN.md` suffix. Both pages are published at distinct URLs, and each translated page links directly to its counterpart so readers can share a locale-specific URL.

## Completed entry pages

The repository README, documentation index, platform overview, installation guide, first-backtest tutorial, results guide, glossary, language policy, common entry points, public API reference, allocation reference, position output contract, data boundary, backtest configuration reference, backtest specification, execution-cost assumptions, cost breakdown, testing and quality checks guide, orchestration overview, control-plane API, evaluation orchestration, orchestration reference index, orchestration configuration reference, and orchestration CLI-helper reference have English canonical pages and linked Chinese companions. The other orchestration guides remain Chinese originals pending translation. MkDocs uses English as its default interface language.

## Remaining work

Many active MkDocs pages are still Chinese-only. Untranslated pages remain grouped as Chinese originals while translation is in progress. Prioritize pages by reader impact:

1. Configuration, CLI, and data-contract references.
2. Backtest specifications, execution and cost assumptions, output contracts, and operational runbooks.
3. Alpha and research-concept pages that are part of the public product surface.
4. Historical migration records and archived plans, after active user-facing docs are complete.

Do not create an English page by translating stale prose alone. Verify each page against current code, configuration, CLI help, tests, and artifacts. Keep identifiers and machine-readable contracts unchanged. Update this tracker as paired pages are added, and ensure the Chinese companion remains consistent with the English source.
