# Historical migration material

This directory preserves read-only copies of former `alpha-research`, `portfolio-backtester`, `quant-execution-engine`, and `strategy-pipeline` repository trees for historical comparison. These copies are not current APIs, supported development entry points, or the source of truth for present behavior.

## How to use the archive

1. Start with the current [platform documentation](../../README.md), [namespace migration](../../namespace-migration.md), and [ownership migration](../../ownership-migration.md).
2. Open a legacy copy only to reproduce a historical implementation, inspect a migration decision, or compare behavior.
3. Confirm current behavior in the active source paths listed in the current documentation. Do not copy an archived implementation into active code without checking current ownership, contracts, and dependencies.

The private `quant-research` repository maintains the cross-repository [historical index](https://github.com/runchengxie/quant-research/blob/main/docs/migration/HISTORICAL-RESEARCH-INDEX.md) and item-level inventory. This local archive is retained for traceability; deleting it is not part of routine maintenance.
