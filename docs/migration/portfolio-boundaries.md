# Portfolio ownership and compatibility migration

Language: English · [简体中文](portfolio-boundaries.zh-CN.md)

The historical `packages/portfolio-backtester` directory is retired. Platform
source now lives under `packages/platform/src`. This is an ownership and dependency
migration, not a claim that Rust reproduces every historical Python simulation.

## Public owners

| Import | Responsibility |
| --- | --- |
| `quant_backtest_engine.EngineClient` | Independent stdlib wire SDK, executable pinning, sizing/session protocol validation; returns JSON-compatible dictionaries |
| `quant_platform.backtest.engine_sessions.EngineClient` | SDK composition and canonical pandas conversion only |
| `quant_platform.backtest.contracts` | Canonical result types, backend protocol and registry |
| `quant_platform.backtest.ledger` | Neutral ledger data shape and reconciliation |
| `quant_platform.portfolio` | Portfolio construction, allocation and optimization APIs |
| `quant_platform.analytics` | Metrics, attribution, risk and reporting APIs |
| `quant_platform.backtest.legacy` | Explicit Python compatibility backends and retained simulation workflows |

Public owner submodules preserve the familiar module names, for example
`quant_platform.analytics.metrics`, `quant_platform.portfolio.optimization`, and
`quant_platform.backtest.legacy.execution_sim`. The old namespace remains as explicit
compatibility aliases. Exported functions/classes share one implementation; regular
module aliases preserve monkeypatch identity. Package proxies retain their own
search path so old child imports resolve to the intended aliases. There is no global
import hook or duplicate algorithm. Historical serialized identifiers retain their original meaning. New minute checkpoints use
Engine v3 and reject historical v2 checkpoints.

The coherent historical implementation is temporarily internal at
`quant_platform._portfolio`. It is not a public API. Public facade imports are lazy;
importing neutral contracts or numerical metrics must not load the legacy simulator.
Keeping this internal graph intact lets callers migrate without simultaneously
rewriting hundreds of relative imports and financial algorithms.

## Caller changes

Platform 0.1.0 installs core 0.1.0 [minute,cost,scenario] and SDK 0.3.0 from
merged Engine revision `19a2ae714b567fc1a46cf996fa5a86a90138bc44` on Python
3.12/3.13. Run `uv sync --locked`; the `engine` extra remains a compatibility
selection. A Rust executable is required only for explicitly selected Rust jobs.
The SDK remains independently installable without Platform or the Python core.
Minute execution, events, impact and leaf evidence APIs now alias Engine objects.
Statistical risk and generic portfolio optimization remain Platform-owned.

```python
# New analysis callers
from quant_platform.analytics.metrics import summarize_ic
from quant_platform.backtest.contracts import CanonicalBacktestResult

# Existing Python execution workflow, explicitly identified as compatibility
from quant_platform.backtest.legacy.execution_sim import ExecutionSimConfig

# Independent raw wire client (no platform install needed)
from quant_backtest_engine import EngineClient as WireEngineClient
```

For deep imports consult the checked-in
[module map](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/portfolio-module-map.json).
Platform orchestration uses these owners. `scripts/dev/check_legacy_imports.py`
rejects direct old-namespace imports in first-party production code. External callers
can still use old imports while migrating; compatibility tests intentionally keep them.
The neutral contracts and wheel import checks are independent of the old package.

## What remains Python, and why

Corporate actions, receivables, delisting policies, daily participation/capacity,
dated fees and full historical execution-evidence workflows retain their tested
Python paths until the specific caller has a verified replacement. Configured T+1,
quote permissions and daily engine balances do not prove parity for those mechanisms.
The Rust adapter still reports `execution_aware=False` and supplies no fabricated
full unified ledger. Planned sale cash remains an estimate; execution is authoritative.

Runtime installs its old backends through an explicit `legacy` extra; Rust-only
jobs do not require the platform package. Historical protocols, request hashes and
result readers remain compatible. A missing optional dependency is an actionable
failure rather than an implicit fallback to a different financial model.

## Final removal gates

The directory move is complete, but the compatibility namespace is not deleted.
Before retiring an individual Python calculation or its old import path:

1. Inventory actual callers, including scheduled release paths and external users.
2. Map required time semantics, settlement, fees, corporate actions and outputs.
3. Compare matched synthetic cases, cash/shares/fills and representative workflows;
   explain differences and verify complete evidence mapping where required.
4. Merge provider versions before updating consumer pins; record tested revision pairs.
5. Verify clean wheel installs, old-result reading and documented historical reproduction.
6. Keep aliases for at least two minor-release cycles and until all recorded supported
   consumers have migrated. Announce the breaking import removal in a versioned release after compatibility
   obligations are retired. Removing an alias must not remove unrelated analytics.

No live job, production release, dataset or scheduled path is switched by this source
migration. Repository import inventories cannot establish that all external or deployed
callers have disappeared. Their inventory is a separate retirement requirement.

Historical minute v2 recovery requires the original pinned full Runtime/Go/Python
release and dependency closure. Keep its source, binaries and bindings fixed.
Installing an old Platform wheel alone does not establish operational recovery.
