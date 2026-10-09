# Research Assurance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver all five approved assurance flows with consumer-level evidence.

**Architecture:** Extend current owners and contracts. Merge public providers before pinning their revisions in consumers; keep independent model research usable without platform imports.

**Tech Stack:** Locked Python environments, pandas/NumPy, SQLite, pytest, existing CLI/artifact interfaces.

**Spec:** [Approved design](../specs/2026-10-09-research-assurance-design.md).

## Global Constraints

- Adding an unused utility or writing a checklist alone does not complete a flow.
- Do not use sibling source imports or unpublished development refs.
- Synthetic evidence establishes software behavior, not investment performance or calibrated real-market costs.
- Runtime signal/resource tests require Linux.
- Production rollout remains separate from repository merge.
- Paths in subplans are relative to the named repository. Follow each AGENTS.md, use isolated worktrees and preserve current callers.

## Review Focus

- Existing v1 callers must pass after optional extensions.
- Consumers must pin merged providers, not working branches.
- Missing evidence cannot be reported as ready/calibrated.
- Linux/native skips cannot be counted as behavior verified.
- Each flow must have an actual CLI/consumer and a merged implementation PR.

## Subplans and order

1. [Scenarios](2026-10-09-assurance-scenarios.md), Tasks 1-2: public factories and consumer truth tests.
2. [Information time](2026-10-09-assurance-information-time.md), Task 1: public revision selection.
3. [Cost and capacity](2026-10-09-assurance-cost-capacity.md), Tasks 1-2: public evidence contracts.
4. Merge provider; complete information-time, cost and scenario research/model consumers.
5. [Trial accounting](2026-10-09-assurance-trials.md): private lifecycle wrapper and model export.
6. [Recovery](2026-10-09-assurance-recovery.md): Linux worker faults and sender/recovery behavior.

Platform additions may share one provider PR. Consumer repositories each have their own PR. Keep research changes in one task worktree to avoid competing lockfile edits. Update quant-platform and research-contracts pins together where both are pinned. Deep learning receives no platform dependency.

## Delivery gates

- [ ] Public provider: locked all-groups sync, Ruff, pytest and applicable native parity; merge PR.
- [ ] Research: production Ruff baseline, documentation checker, affected/full related pytest layers; merge consumer PR with exact provider pin.
- [ ] Deep learning: Ruff, format, ty, notebook lint, coverage pytest, smoke and web tests/build; required CI before merge.
- [ ] Runtime: Linux Ruff/ty, coverage tests and synthetic CLI smoke; verify Python 3.12/3.13 CI. No working WSL was found locally; retain the PR if Linux validation is unavailable.
- [ ] Intel: complete owner-local project_tools/check_all.py --scope all, delivery/recovery regressions and required CI.
- [ ] Record all five flows' PRs, merge SHAs, commands, exit codes, counts, skips and blockers in an external delivery ledger.
- [ ] Fast-forward clean primary checkouts and clean only this task's merged worktrees/branches; preserve unique or unmerged work.

## Execution handoff

Recommended: Native execution in this session, with one fresh whole-change reviewer at the end. Contracts, version pins and persistence boundaries benefit from sequential coordination. Subagent-driven execution adds independent implementation/review gates for each task. Await plan review and execution-method selection before product implementation.
