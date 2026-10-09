# Trial Accounting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Record attempts before execution and export complete family/run accounting.

**Architecture:** Private SQLite lifecycle events project to existing trial_ledger_entry.v1. Independent model registry gains reporting and recovery coverage, not replacement.

**Tech Stack:** SQLite transactions, subprocess argument arrays, pytest.

**Spec:** [Approved design](../specs/2026-10-09-research-assurance-design.md).

## Global Constraints

The [master plan](2026-10-09-research-assurance.md) applies. Preserve existing exclusion rules and locked-data controls. Hard termination leaves an unfinished attempt, not a fictitious terminal success.

## Review Focus

- No-summary failures remain recorded (Task 1).
- Same ID with changed metadata cannot overwrite (Task 1).
- Competing state transitions cannot lose events (Task 1).
- Poor results remain counted (Task 2).
- Export does not consume locked approval or reveal artifact contents (Task 3).

### Task 1: Lifecycle store and legacy export

**Files:** quant-research: create src/strategy_research/trial_lifecycle.py and tests/strategy_research/test_trial_lifecycle.py; reuse scripts/validation/_trial_ledger_check_core.py.

**Interfaces:** TrialLifecycle(database: Path); reserve(entry: Mapping[str, object]) -> None; transition(trial_id: str, *, expected_state: str, state: str, updates: Mapping[str, object]) -> None; latest_entries() -> list[dict[str, object]]; export(path: Path) -> None. SQLite append-only events and latest projection. Existing proposed/running/completed/failed/invalid states.

- [ ] Test reservation before execution, exact reserve retry, changed identity conflict, terminal regression rejection, two competing transitions, unfinished running state and one-record-per-trial export through existing validator.
- [ ] Run uv run pytest tests/strategy_research/test_trial_lifecycle.py -q and confirm missing store fails.
- [ ] Implement immutable metadata, UTC events and transactional compare-and-swap projection. Atomically export latest states without rewriting historical ledgers.
- [ ] Pass new tests and existing trial ledger/CLI/registry migration tests.
- [ ] Commit: feat: persist complete trial lifecycle.

### Task 2: Controlled execution, recovery and family report

**Files:** quant-research: create src/strategy_research/trial_lifecycle_cli.py, tests/strategy_research/test_trial_lifecycle_cli.py and docs/research/trial-lifecycle.md; modify pyproject.toml and uv.lock.

**Interfaces:** research-trial run --database PATH --entry PATH --executor cashflow-platform-replay -- ARGS; recover --trial-id ID --reason TEXT; export --output PATH; family-report --family ID. Only the existing cashflow replay executor is initially allowlisted, invoked without shell interpretation. Reports distinguish failed/rejected/unfinished, excluded and unaccounted legacy attempts.

- [ ] Test synthetic real subprocess success/nonzero exit, unsupported executor, pre-summary interruption, idempotent explicit recovery, retained poor results and unfinished family counts. State that family counts alone are not corrected significance.
- [ ] Run uv run pytest tests/strategy_research/test_trial_lifecycle_cli.py -q; confirm missing CLI behavior fails.
- [ ] Persist proposed/running before child launch, preserve child exit code, record failure, and route a documented existing replay example through wrapper. Recovery never rewrites completed trials.
- [ ] Pass lifecycle/ledger tests and replay regressions; verify --help and full synthetic wrapper/export example.
- [ ] Commit: feat: run research through accountable trial wrapper.

### Task 3: Independent model accounting export

**Files:** quant-deep-learning: create src/ticknet/research/trial_accounting.py and tests/test_research_trial_accounting.py; modify src/ticknet/research/cli.py; extend existing registry/runner tests and docs/operations/development-guide.md.

**Interfaces:** export_trial_accounting(registry: ExperimentRegistry, *, family_by_experiment: Mapping[str,str]) -> dict[str,object]. Schema ticknet.trial-accounting.v1; report experiment/run states and explicit family mapping. Add existing research CLI export subcommand.

- [ ] Test pre-execution rejection, executor failure, running interruption, completed seeds, unmapped family and consistent registry read snapshot. Export never consumes locked approvals.
- [ ] Run uv run --locked --extra dev pytest tests/test_research_trial_accounting.py -q; confirm missing export fails.
- [ ] Query existing registry in a read transaction, preserve independent schema and expose missing recovery state only if current API cannot express it.
- [ ] Pass export plus test_research.py, test_research_cli.py, protocol/approval/orchestrator regressions.
- [ ] Commit: feat: export model trial accounting.
