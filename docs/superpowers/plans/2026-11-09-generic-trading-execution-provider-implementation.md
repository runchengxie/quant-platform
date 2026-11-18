# Generic Trading Execution Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. One product implementer at a time; independently review each task and the whole provider. The owner requested responsibility-based extraction, with standing reviewed-PR integration authorization.

**Goal:** Publish the existing public generic order-lifecycle library independently, without private broker adapters or implicit state-directory changes.
**Architecture:** A new quant-trade-execution/quant_trade_execution0.1.0 provider owns generic OMS, domain/risk/state/reconciliation and offline mock behavior. Engine owns financial backtesting. Default wheels use the canonical namespace; legacy aliases wait for the coordinated consumer profile.
**Tech Stack:** Python3.12+, stdlib base, optional existing Rich rendering, installed wheels, synthetic offline tests and ordinary GitHub CI.
**Spec:** [English package design](../specs/2026-11-09-package-ownership-design.md) · [中文设计](../specs/2026-11-09-package-ownership-design.zh-CN.md).

## Global Constraints

- The proposed implementation name for the new generic library is quant-trade-execution, distribution quant-trade-execution, canonical namespace quant_trade_execution, initial version0.1.0.
- Use only the already-public source closure.
- Actual Alpaca/IBKR/Longport implementations stay private.
- No request-selected imports/commands and no fake SDK fallback may report successful trading capability.
- Base imports must not import private Research, model training, Runtime or network clients and must not create state directories or probe broker accounts.
- No implicit new path may hide existing pending orders by creating an empty account.
- Preserve order/account identities, idempotency, reservations, kill switches, cancel/recovery semantics and complete trace/state outputs.
- An execution mock and an Engine account must not become two cash ledgers for one run.
- Keep raw data, runtime results and credentials outside repositories.
- Keep aliases for at least two minor cycles and until all recorded supported consumers migrate or have an explicit pinned legacy environment.
- Every transfer preserves original license/copyright and per-file provenance.
- No broker login/order, actual paper order submission, credentials, production configuration/scheduler/current switch, live model training or real-data acquisition is authorized by this code migration request.

## Review Focus

1. Merely importing paths creates a new empty account beside pending orders: no import writes, fresh roots explicit and old resolved roots unchanged (Tasks1–2).
2. A missing vendor SDK falls back to a mock success: only offline mock/explicit trusted injected adapters supported (Tasks1–3).
3. A relocation changes serialization, idempotency, reservations or recovery ordering: compare complete traces/state and failures, not just final balance (Tasks2–3).
4. Old and new wheels overwrite quant_execution_engine files or recreate classes: canonical-only provider first, alias profile later with one file owner (Task4).
5. A private adapter/configuration leaks into the public repository: public Git source allowlist/source provenance and no reverse imports (Tasks1–4).

## Preparation and release boundary

T=new provider; P=quant-platform. P source reference7a618bddd8fdeee5dbe37fe5b54a9698e0de5355. Read/refresh the public execution inventory before code; record the current actual source if P advances. All69 Python files under P/packages/execution/src/quant_execution_engine are the candidate closure; they contain only stdlib imports plus optional Rich in renderers/diff.py, as observed by AST inventory. Dynamic imports/factory semantics still need inspection; AST findings are not a capability proof.

Verify runchengxie repository ownership/name availability using configured gh authentication before creating the repository. Preserve an existing repository if found; do not revive the retired quant-execution-engine checkout. For a genuinely new repository, seed a minimal README/Apache2 source-license/AGENTS main, then use a task branch and isolated worktree for the implementation PR. No forced push or protected-control bypass. The initial public library contains no real account config, vendor adapter, credential helper or live-order CLI.

T AGENTS/CI gates must cover Ruff/format/type checking, full synthetic tests, stdlib installed base and optional renderer profile, source-boundary/license/RECORD checks and Python3.12/3.13. Pin actual tooling through the lockfile rather than silently using changing latest tools. Project data/environments/builds live under its own external DATA root. No PyPI publication or deployment activation.

## Task 1: Provider foundation and explicit boundaries

**Files:** Create T/pyproject.toml, uv.lock, src/quant_trade_execution/{__init__,paths,config}.py, packaged source/license notices, tests/test_import_boundaries.py, tests/test_paths.py, .github/workflows/ci.yml and paired docs/installation guides.

**Interfaces:** Preserve source public names/signatures where already defined. Canonical root/config resolution is explicit at application construction; importing any base module creates no directory and reads no credentials/accounts. Existing QEXEC_OUTPUTS_DIR/QUANT_PLATFORM_OUTPUT_ROOT/DATA_PLATFORM_ROOT/XDG fallback behavior is recorded as the legacy profile, not silently repointed to a new empty root. No network provider is selected during import.

- [ ] RED subprocess tests run import in an empty task-owned home/state directory with network blocked and assert no files/directories/probes; exercise explicit roots, missing/invalid config and pre-existing pending-state sentinel preservation.
- [ ] Establish canonical package/config/path boundaries, with directories created only for an explicit write operation. Keep legacy historical state in place.
- [ ] Record the full original public file/symbol/license inventory and capability table. Inspect public factory/_stubs: identify actual mock/injection paths and make unavailable vendors fail explicitly.
- [ ] Run focused base/path tests and required initial quality checks; paired docs state real scope and old recovery limits. Commit and independent review.

## Task 2: Domain, risk, serialization and state closure

**Files:** Transfer the cataloged public _domain_*, _serialization_*, _state_* helpers and account/domain/models/fees/fx/guards/risk/risk_pipeline/serialization/execution_state/state_tools/diagnostics/health/preflight/lifecycle/runtime_events modules into T/src/quant_trade_execution with their complete local imports. Port matching public P execution tests into T/tests, keeping synthetic inputs.

**Interfaces:** Preserve exact enums, IDs, decimal/rounding meanings, schema versions, state keys, reservation/risk decisions and exception categories. Existing serialized history retains original producer identity; no hot-restore claim across relocated providers. Config/path construction uses Task1's explicit boundary. Namespaces change without duplicate class definitions.

- [ ] RED regression tests cover schema1/schema2 payloads, rejected malformed/nonfinite state, account/order identity, unavailable funds and reservation release, kill switches and pending/cancel states.
- [ ] Port complete helper closures without arithmetic/order rewrites; audit normalized AST bodies against the pinned original, documenting only explicit path/import/capability differences.
- [ ] Compare complete old/new serialized state and public payloads under fixed synthetic clocks/IDs in separate installed reference/provider environments.
- [ ] Run focused/full affected tests, installed base import checks and paired API/migration docs; commit and independent review.

## Task 3: OMS services, recovery and deterministic offline peer

**Files:** Transfer remaining cataloged public execution_service/recovery/reconcile/rebalance/execution/facade/evidence/handoff/targets modules, their underscore helpers, broker/{base,factory,mock_sim,_stubs,__init__}.py and optional renderers into the canonical namespace. Add tests/test_offline_lifecycle.py, test_recovery_parity.py and test_provider_injection.py plus paired capability/recovery guides.

**Interfaces:** Existing BrokerAdapter/domain/order lifecycle signatures stay intact. Supported capabilities are offline mock and an explicitly injected trusted host adapter implementing the typed interface; no manifest chooses arbitrary imports. Rich rendering is optional and lazy. Mock venue persistence is an OMS test peer, not a calibrated financial backtest or real broker account.

- [ ] RED full lifecycle tests cover submit/retry/duplicate/cancel/replace/fill/reconcile/reservation/restart at each state boundary, injected original failures and typed adapter rejection.
- [ ] Preserve public source bodies except explicit namespace/path/unavailable-provider changes. Do not copy private vendors or add live-order command entry points.
- [ ] Compare full offline event traces and serialized state against the pinned public original; run two independent mock accounts to prove isolation and no extra Engine cash ledger.
- [ ] Exercise unavailable vendors without credentials/network; prove no mock fallback. Test trusted adapter injection with synthetic public peers, not real vendor login.
- [ ] Run all affected gates and optional-renderer tests, command/API docs checks and source-boundary/license audits; commit and independent review.

## Task 4: Standalone installed release

**Files:** Finish source inventory and dependency/package/CI metadata, project_tools/verify_installed_execution.py, tests/test_wheel_ownership.py and paired README/migration/installation references.

**Interfaces:** The default quant-trade-execution0.1.0 wheel owns only quant_trade_execution; it does not yet ship quant_execution_engine. Formal installations run outside source with -I, actual merged VCS/wheel identity, no Platform/Engine/Runtime/Research/training/vendor SDK dependency. Source-specific original Apache notices ship in the actual wheel.

- [ ] RED installed checks reject editable/source imports, missing helpers/license files, private/vendor imports, import-created state and wheel/CLI overlap with the retained P legacy provider.
- [ ] Build actual wheels and run complete synthetic lifecycle/recovery/API acceptance on fresh Python3.12/3.13 base environments and optional-renderer profiles; record source/dependency/wheel/origin identities.
- [ ] Whole-provider review and current-target required PR checks precede merge. Verify actual merged install and original-source parity; clean only this task's merged resources.
- [ ] Record the exact release for downstream private typed adapters and Platform. Do not activate any account, move existing state or claim real broker validation.

## Subsequent compatibility and consumer gate

A separate opt-in alias distribution in this owner may provide thin quant_execution_engine modules only after the pruned Platform candidate and private adapter consumers are ready. Audit RECORD/entry points and class identity in fresh combined profiles; aliases must reference the canonical classes, not copied definitions. Platform cannot depend on an unmerged provider and no public provider imports private Research. Old recordings/checkpoints retain their full pinned environment. Legacy-root state handoff and any live operational activation remain separately authorized operations after a concrete tested proposal.

## Controller self-review

Tasks1–4 cover the full public generic closure and explicit operational boundaries; the optional legacy profile/private consumers are separate active cuts. Every review failure class has a named meaningful regression. The plan introduces no new execution model, backtest account, real adapter, credential behavior or production scheduler.
