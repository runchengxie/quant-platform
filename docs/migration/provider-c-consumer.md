# Provider C consumer contract

[简体中文](provider-c-consumer.zh-CN.md)

Platform 0.3.0 delegates daily/period financial work to merged Engine `ad0895f1c2015eb31bd364b40741b0f7cd6e0048` (Core and SDK 0.3.0). Target construction, research statistics, provider calendar lookup and publication remain Platform responsibilities. Legacy accounting functions with different normalization semantics retain their distinct Core identities.

The implementation sequence is: retain the original public-workflow oracle, verify missing adapters fail, pin both merged providers, replace kernels with aliases, restore original research reporting, then validate complete public outputs, installed Python 3.12/3.13 consumers and paired documentation. Kernel authority is recorded in [test provenance](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/engine-provider-c-test-provenance.json); retained Platform tests exercise public integration rather than a second financial implementation.

The API amendment is compatible: `to_canonical_result(result, *, artifact_root: Path | None = None)`. One-argument normalized evidence remains conservative. Explicit-root full raw conversion validates relative URI, digest, media, schema and supported dtype without evaluating serialized code. Structural table completeness, valuation completeness and canonical ledger representability are independent. Missing marks and receivables cannot become supported cash or returns merely because raw tables exist. See [daily consumers](../backtest/engine-daily.md).

Acceptance compares original native/sequenced/position/top-k returns, periods, research summaries and all eight ledger fields without dtype exceptions. It includes independent hand oracles, serialized IDs, actual native/Rust execution and explicit refusal to publish incomplete evidence. Historical direct-API statistics keep their old formulas and limitations.

External cohorts must be reported individually. A direct compatibility seam is not an executed Runtime job, and a source pin is not a restored executable closure. Deep-learning signal acceptance still hard-pins Platform/contracts `282afca4c4ca210d46eed096a943972662fede99`. Market synthetic-chain admission has its own historical multi-repository pins; microcap diagnostics require Runtime. Their full legacy Runtime/Go/Python restoration remains pending Tasks 16–17. Keep every compatibility alias for at least two minor releases and until all supported consumers migrate. This wave does not migrate production, broker connections or checkpoints.
