# Synthetic Scenarios Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Export deterministic scenarios with known truth and verify existing consumers.

**Architecture:** Lightweight public factories in quant-platform; downstream tests use the public package or artifact contract. No Torch, GPU or real data is required.

**Tech Stack:** pandas/NumPy, canonical JSON/CSV, pytest, optional native parity.

**Spec:** [Approved design](../specs/2026-10-09-research-assurance-design.md).

## Global Constraints

All constraints and delivery gates in [the master plan](2026-10-09-research-assurance.md) apply. Synthetic truth is software evidence only.

## Review Focus

- Same seed produces identical hashes (Task 1).
- Existing destinations and path traversal are rejected (Task 1).
- Tampered artifacts fail before consumption (Task 1).
- Null truth uses constructed outcomes, not random performance thresholds (Task 2).
- Sequence gaps stay visible; missing Rust is a skip (Task 2).

### Task 1: Factory, export and CLI

**Files:** quant-platform: create packages/portfolio-backtester/src/quant_platform/scenarios.py, tests/test_assurance_scenarios.py and docs/guides/assurance-scenarios.md.

**Interfaces:** ScenarioBundle(name: str, seed: int, frames: dict[str, pd.DataFrame], truth: dict[str, object]); build_scenario(name: str, *, seed: int = 0) -> ScenarioBundle; write_scenario(bundle: ScenarioBundle, destination: Path) -> Path; read_scenario(manifest: Path) -> ScenarioBundle. Schema quant.assurance-scenario.v1. Names: null_signal, industry_confound, delayed_revision, partial_fill, sequence_gap. CLI: python -m quant_platform.scenarios NAME --seed N --output DIR.

- [ ] Write tests for round-trip of all five scenarios; same-seed byte/hash equality; changed seed changes numeric input; refused overwrite; missing/tampered files; traversal rejection.
- [ ] Run uv run pytest tests/test_assurance_scenarios.py -q and verify the missing implementation fails.
- [ ] Implement deterministic frames and canonical JSON/CSV inventory with seed, input hashes and explicit truth. Null data uses orthogonal predictions/returns; industry data's return depends solely on sector; revisions have two availability times; partial fills declare expected accounting; gap manifest names its missing sequence.
- [ ] Run the tests and existing PIT/ledger tests; require exit 0. Check CLI --help and export/reload example.
- [ ] Commit: feat: add deterministic assurance scenarios.

### Task 2: Consumer truth and native parity

**Files:** quant-platform: create tests/test_assurance_scenario_consumers.py; extend tests/microstructure/test_rust_parity.py and the scenario guide.

**Interfaces:** Consume Task 1 read_scenario through existing PIT view, attribution/neutralization, ledger and event-ordering interfaces.

- [ ] Write tests asserting exact zero covariance for null truth, removed constructed sector effect after neutralization, declared partial-fill accounting and flagged sequence incompleteness. Add equivalent Python/Rust replay case when native backend exists.
- [ ] Run uv run pytest tests/test_assurance_scenario_consumers.py tests/microstructure/test_rust_parity.py -q; establish failing/new coverage before changing consumers.
- [ ] Implement consumer adaptations only where new assertions expose missing behavior. Keep sequence evidence unsorted/unrepaired and native imports isolated.
- [ ] Pass the same command and existing ordering/matching/replay regressions; report native skips explicitly.
- [ ] Commit: test: verify scenario truth through public consumers.

### Task 3: Independent model artifact consumption

**Files:** quant-deep-learning: create src/ticknet/research/scenario_contract.py and tests/test_assurance_scenario_contract.py; extend docs/operations/development-guide.md.

**Interfaces:** load_scenario(manifest: Path) -> tuple[dict[str, pd.DataFrame], dict[str, object]], reading quant.assurance-scenario.v1 without importing quant-platform. It verifies schema, inventory hashes, containment and declared truth before returning frames. No new dependency is needed.

- [ ] Write tests with small synthetic manifest/CSV fixtures matching Task 1's published format: delayed revision, null truth, tampering and path traversal. Feed returned identities/windows into the existing prediction-audit or horizon-selection path; malformed inputs fail before evaluation.
- [ ] Run uv run --locked --extra dev pytest tests/test_assurance_scenario_contract.py -q; confirm absent reader fails.
- [ ] Implement only the independent artifact reader and consumer adapter. Run a public factory export through the reader as a cross-repository smoke using the released CLI, not sibling source imports.
- [ ] Pass the new tests and affected research-audit/horizon tests. Record the producing platform commit and input hashes in smoke evidence.
- [ ] Commit: feat: consume public assurance scenario artifacts.
