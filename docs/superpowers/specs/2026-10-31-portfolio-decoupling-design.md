# Portfolio implementation decoupling

The independent engine is an opt-in upstream adapter, not feature parity with all historical Python workflows. Retire the historical directory and direct consumer dependencies without deleting required behavior.

## Approach

Move the implementation intact to `packages/platform/src/quant_platform/_portfolio`, keeping relative imports coherent. Explicit `quant_platform.portfolio`, `quant_platform.analytics` and `quant_platform.backtest.legacy` module facades declare supported ownership. Preserve old deep imports with individual module aliases; no global import hook or duplicate simulator. This reduces regression risk compared with rewriting all internal relative imports while splitting 192 modules simultaneously. The private implementation package is an extraction boundary, not a stable public API.

Move canonical result types, UnifiedLedger data shape and pure reconciliation into `quant_platform.backtest` without imports from the old simulator. Generic subprocess calls and raw result validation belong to the independent engine's stdlib Python SDK. Platform retains only canonical dataframe mapping; its old client path remains compatible.

Migrate first-party source callers to explicit public owners. Keep old schemas/field names, economic results and legacy module aliases compatible. Preserve Python corporate actions, delisting, capacity and rich evidence until their actual workflow replacements are proven. Do not label namespace relocation as Rust parity.

Runtime has no mandatory platform dependency; an explicit legacy extra supplies old job backends. New Rust jobs and discovery must work in a clean minimal wheel install.

## Completion gates

Provider SDK merges before platform SDK pin; platform facades merge before research callers pin the provider. Full platform tests/static checks, built wheel import isolation, module identity/monkeypatch and schema compatibility tests, real engine integration, runtime lean/full environments, consumer relevant/full suites and public migration records must pass. No production schedule or dataset is changed. The old compatibility namespace is removed only after first-party and external compatibility obligations are retired; this task instead installs a ratchet against new first-party old imports and records remaining feature gaps.
