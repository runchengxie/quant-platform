# Orchestration

`strategy_pipeline` provides reusable run control, artifact publication,
quality gates, receipts, and owner handoff contracts. Strategy-specific logic,
private data providers, and production scheduling remain outside this public
package.

The existing `strategy-pipeline` Python namespace and CLI are preserved during
the migration.
