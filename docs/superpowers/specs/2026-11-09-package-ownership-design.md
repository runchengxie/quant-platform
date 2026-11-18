# Package ownership after the backtesting extraction

[简体中文](2026-11-09-package-ownership-design.zh-CN.md)

Status: the owner requested implementation of the role-based split on 2026-11-09. This design records the implementation defaults and compatibility gates. Existing Engine and report-publication work remain active. No broker access, order submission, production switch, real training or data acquisition is authorized by this code migration.

## Intended result

Platform contains reusable portfolio/risk/analysis mechanisms and explicit consumer adapters. Models, backtest financial owners, workflow coordination and generic order-lifecycle services have independent owners and tested installation boundaries. Directory names are not ownership evidence; a move is complete only when code, tests, documentation, installed consumers and historical recovery routes agree.

The existing Engine extraction remains the sole implementation of its simulation transfers. Do not duplicate that work or change its approved arithmetic and checkpoint boundaries in this project.

## Source evidence and approaches

The read-only inventory at Platform 7a618bd found 35 Python microstructure files, 33 orchestration files and 69 execution files. The source-line total is approximately 27,000, including comments/blank lines. Of 26 same-path files in Deep Learning, five have identical bytes; differences need API/protocol inspection before replacement. Static imports occur in 275 files including internals and tests; that is not a deployment census.

| Approach | Tradeoff | Choice |
| --- | --- | --- |
| Move the three directories wholesale to three similarly named repositories | Low initial effort, but moves training into workers and broker services into a backtester | Rejected |
| Keep all implementations in Platform behind new frontends | Preserves coupled dependencies and overlapping namespace owners | Transitional frozen legacy only |
| Extract complete responsibility closures, publish providers first and migrate consumers | More compatibility work; produces independent tested libraries | Selected by the owner's requested role-based split |

Real broker adapters already live in the private execution owner. Public Platform contains generic BrokerAdapter/domain/order-state services, a deterministic mock broker and factory hooks. Public extraction must not copy private adapters, credentials or strategy configuration.

## Target responsibilities

| Responsibility | Owner |
| --- | --- |
| Model-specific datasets, labels, representations, training, prediction and model evidence | quant-deep-learning |
| Matching/replay/native matching extension, simulated impact, financial accounts/sessions, execution planning and scenarios | quant-backtest-engine, through its existing approved plan |
| Strategy/research training flow, OOS selection, admission, promotion and authoritative research records | quant-research |
| Cross-owner DAG, plan approval, audit and coordination | quant-task-orchestrator |
| Backtest queue, worker, leases, resource limits, crash admission and result durability | quant-backtest-runtime |
| Generic order-lifecycle/domain/risk gates/reconciliation and offline mock venue | Independent trading execution library |
| General portfolio/risk/statistical primitives and result analytics | quant-platform |

The proposed implementation name for the new generic library is quant-trade-execution, distribution quant-trade-execution, canonical namespace quant_trade_execution, initial version 0.1.0. This is a controller default for a new independently installable public provider, not an existing deployed repository or an owner-confirmed spelling. Reserve/verify the user's repository before creating it; use only the already-public source closure. Do not revive a retired historical checkout or add a live-order CLI just to rename code.

## Microstructure and model convergence

Deep Learning is the canonical training owner. For every divergent module, inventory public symbols, input and checkpoint schemas, functional differences and callers. Preserve current canonical model work and any useful Platform-only changes through reviewed owner changes. Do not blindly replace current code with an older copy.

Model methods, weights/shapes, labels, split discipline, clocks and forecast artifacts keep their meaning. Existing results/checkpoints retain the actual original producer/source/dependency identity. Equal schema strings do not establish restore compatibility. Unsupported old checkpoints keep a complete pinned legacy environment; no history or checkpoint metadata is rewritten.

Deep Learning declares Python 3.10+, while some Platform modules use 3.12-only typing/features. Preserve its supported boundary through compatible imports/annotations where possible and run actual relevant 3.10 checks as well as current CI. A necessary support-profile change must be explicit and independently validated, not silently inferred from Platform's floor. No real training or new empirical result is needed for an ownership move.

Engine's independent quant_backtest_core simulator/native provider must be merged before new simulation consumers switch. Keep training dependencies out of Engine/base Platform imports. The native extension is not Nautilus and must retain its own distribution/identity and licenses.

## One owner for every installed namespace file

Audit wheel RECORD files and console entry points, not just repository paths.

- Deep Learning owns ticknet root/model/dataset/eventstream files. Its owner-side optional lazy ticknet.simulator compatibility shims may delegate to the merged Engine provider. Platform stops shipping all ticknet files after the supported caller cohort is migrated. The optional compatibility installation explicitly supplies Deep Learning and Engine; basic Engine matching stays Torch-free.
- Task Orchestrator owns canonical coordination APIs and the lightweight legacy strategy_pipeline root/control_plane shims. These must not import private Research or grant durable workflow approvals. Research may supply nonoverlapping legacy strategy_pipeline.pipeline child modules for its explicit installed research profile. Each physical file has one wheel owner; installed parent/child discovery and uninstall/dependency behavior must be tested.
- Research owns the legacy strategy-pipeline training CLI after cutover. Platform stops registering it; Task Orchestrator keeps quant-task for generic workflows. Public Platform does not declare a private package dependency. Known training callers migrate before removal; public users have an explicit pinned legacy route rather than a silently incomplete installation.
- The new execution distribution owns both canonical quant_trade_execution and thin quant_execution_engine aliases. Platform stops shipping those legacy files and consumes the merged provider. Alias classes are identical objects, not copied definitions. Engine financial aliases keep the existing Engine plan's rules.
- Preserve supported aliases for at least two minor cycles and until all recorded supported consumers migrate or have an explicit pinned legacy environment. A namespace file's provider may change while its public import path remains supported; that is not permission to retire the API early.

Research currently also registers some canonical model CLI names. Migrate private-specific commands/callers to explicit research entry points and let Deep Learning exclusively provide canonical model commands. Do not move private model deviations into the public owner. Preserve a full pinned legacy installation for old customized commands; installation order cannot select their semantics.

Never install two wheels that overwrite the same module or CLI. Full noneditable installed-profile tests must prove file ownership, import origin, class identity and dependency closure.

## Strategy pipelines and orchestration

Move research decisions and strategy-specific flow into Research. General date/statistical/portfolio primitives can remain Platform APIs called by the owner; do not copy private strategy implementations into public coordination.

Move truly generic RunOwner/ArtifactPublisher coordination into Task Orchestrator without weakening its existing plan-hash approval and audit contracts. A stateless compatibility helper is not an implicit approval to start a durable research workflow.

Runtime remains a backtest execution consumer. Do not move training, model selection, report composition or promotion into its worker. Cross-owner interfaces use reviewed installed public APIs/CLI or versioned artifacts; no source-tree or private-module import is disguised as a reusable package.

Private consumer file paths, strategy parameters and real trial records remain in private task inventories/Research docs. Public migration tables record roles and public API shapes only. Source-only migration must not re-run or reset authoritative research trials.

## Generic trading execution provider

Extract the complete public generic OMS/domain/model/serialization/risk-gate/state/reconcile/facade/mock closure with original numerical/ordering behavior. Preserve order/account identities, idempotency, reservations, kill switches, cancel/recovery semantics and complete trace/state outputs. Record original Apache source/license provenance.

Actual Alpaca/IBKR/Longport implementations stay private. The standalone public provider exposes only real implemented capability subsets; missing providers fail explicitly. Trusted local callers may inject existing typed adapters. No request-selected imports/commands and no fake SDK fallback may report successful trading capability.

The mock venue is an offline OMS test peer, not proof of a real broker or calibrated backtest economics. Engine remains the quantitative simulation owner. An execution mock and an Engine account must not become two cash ledgers for one run.

Base imports must not import private Research, model training, Runtime or network clients and must not create state directories or probe broker accounts. Small optional config/rendering dependencies retain explicit profiles. Existing QEXEC/config/output root settings and source-relative legacy behavior need an explicit compatibility audit. No implicit new path may hide existing pending orders by creating an empty account. Fresh applications supply external roots; legacy state remains in place until a separately authorized and validated operational handoff.

Old recordings/receipts keep original producer identity, including unknown values. Do not invent a historical source hash or promise hot restore across relocated providers. Test complete old/new offline lifecycle traces, serialized states, failure/restart boundaries and typed private-provider injection before consumer cutover.

## Documentation and public availability

Every transfer preserves original license/copyright and per-file provenance, including model/coordination code moving into owners with a different default license. Ship original terms in the actual wheel and describe the real source-specific combination; do not silently relicense.

Code, acceptance tests, paired EN/ZH installation/API/capability guides, source history links and migration maps move together. Preserve exact old locale routes and stable anchors with owner-correct stubs after the provider is merged. Do not label future provider/compatibility work as installed, released or deployed.

The public registry uses planned/implemented status, real reviewed source revisions, independent release availability and executable acceptance names. No placeholder/self-referential SHA or private caller path. The three responsibilities can have separate provider PRs; Platform consumer cuts follow their actual dependency gates. Update public owner boundaries and installed examples across affected repositories together.

## Rollout and recovery

1. Freeze inventory/oracles and finish the relevant existing Engine simulator/account/provider and Platform consumer cohorts.
2. Converge and publish Deep Learning model APIs/checkpoint disclosures and Engine simulation shims; verify no ticknet file collision.
3. Publish generic Task Orchestrator APIs/legacy root, then private Research pipeline/CLI consumers and independent synthetic research acceptance.
4. Publish the new generic execution library from public-only code, then private adapter injection and Platform legacy imports.
5. Cut remaining Platform implementation/CLI/file ownership after provider merges and installed whole-cohort checks. Keep explicit legacy environments and aliases.
6. Verify current combined main revisions, language routes, docs/builds and task-only cleanup. No production directories, schedules, credentials, active order state or real broker effects change during this work.

Each owner uses its own branch/worktree and required quality gates. Provider revisions and consumer revisions are recorded together. Preserve unrelated/production worktrees and all historical data. Integration follows existing standing authorization; separately gated production actions wait for a concrete tested proposal.

## Acceptance

- No wheel/entry-point overlap; no reverse private/training dependency; standalone provider profiles work outside source with installed wheels.
- Model/API/protocol regression and relevant Python version checks retain existing evidence boundaries; old checkpoint rejection/legacy routes are explicit.
- Workflow approval/audit and Runtime job/result ownership do not weaken; private research trial records are unchanged.
- Original public execution formulas, serialization, idempotency and offline state traces match; unsupported provider requests are honest; no network/order call in tests.
- All recorded static consumers are tested or explicitly pinned; aliases/document routes remain supported. Public inventory contains no private paths/configuration.
- Full affected owner gates and independent reviews pass on the combined target before merge. No actual training, credentials, order submission, production migration or archive deletion is an acceptance shortcut.
