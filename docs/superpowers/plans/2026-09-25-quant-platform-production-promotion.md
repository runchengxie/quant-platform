# Quant Platform Production Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote only the latest fully verified, merged `quant-platform` main commit to its production release directory and confirm rollback readiness.

**Architecture:** Use the deployment repository's existing immutable release and atomic `current` symlink workflow. Pin the source to the exact merged SHA, run dry-run first, publish only `quant-platform`, then verify manifest, symlink, imports, and public contract smoke checks.

**Tech Stack:** Git, GitHub CLI, `promote-production.sh`, Python package import smoke test.

**Spec:** `docs/superpowers/specs/2026-09-25-quality-modularization-and-production-design.md`

## Global Constraints

- Publish only `quant-platform`; do not update other frameworks, schedulers, credentials, research data, or deploy configuration.
- Source must be a clean, merged `main` SHA with all required CI checks successful.
- Do not use temporary worktrees as a production source.
- Preserve the pre-release `current` target and retain three releases when safe.
- If post-release verification fails, atomically restore the recorded pre-release target.

## Review Focus

- The pinned SHA is reachable from `origin/main` and equals the latest merged main commit.
- The deployment source worktree is clean before invoking the publisher.
- Dry-run and actual promotion use the identical full SHA and framework selector.
- The new release manifest and `current` symlink agree on the source SHA.
- Smoke checks import public packages/contracts only and do not start services, research jobs, schedulers, or message delivery.

---

### Task 1: Verify source and rollback targets

**Files:**
- Source repository: `/home/richard/code/quant/quant-platform`
- Deployment guide: `/home/richard/code/quant/quant-intel-deploy/AGENTS.md`
- Publisher: `/home/richard/code/quant/quant-intel-deploy/scripts/promote-production.sh`

**Interfaces:**
- Consumes: all merged implementation PRs and green required checks.
- Produces: exact source SHA, recorded current production SHA, verified rollback path.

- [ ] Run `git -C /home/richard/code/quant/quant-platform status --short --branch` and require a clean `main` checkout.
- [ ] Run `git -C /home/richard/code/quant/quant-platform fetch origin main` and capture `git rev-parse origin/main`.
- [ ] Run `gh -R runchengxie/quant-platform run list --branch main --limit 10` and confirm required checks for that SHA passed.
- [ ] Read the current production symlink and manifest under `/home/richard/code/production/quant-platform/current`; record the exact old SHA.
- [ ] Confirm the recorded old release still exists and its manifest matches before publication.

### Task 2: Dry-run and promote the exact SHA

**Files:**
- Publisher: `/home/richard/code/quant/quant-intel-deploy/scripts/promote-production.sh`
- Production root: `/home/richard/code/production/quant-platform`

**Interfaces:**
- Consumes: Task 1 source SHA and old rollback target.
- Produces: immutable release directory for the exact SHA and atomically updated `current` symlink.

- [ ] Set `release_sha=$(git -C /home/richard/code/quant/quant-platform rev-parse origin/main)` and verify it matches the SHA confirmed in Task 1.
- [ ] Run `PRODUCTION_ROOT=/home/richard/code/production /home/richard/code/quant/quant-intel-deploy/scripts/promote-production.sh --prepare-python quant-platform --dry-run --framework "quant-platform=/home/richard/code/quant/quant-platform@$release_sha"` and inspect the target path and retention actions.
- [ ] Run the same command without `--dry-run`, using the unchanged `release_sha` value.
- [ ] Confirm the publisher reports success and `current` points to the exact newly created release.

### Task 3: Verify release and smoke-test public imports

**Files:**
- Release manifest and contents under `/home/richard/code/production/quant-platform/releases/$release_sha`
- No service entrypoint files

**Interfaces:**
- Consumes: new immutable release and its `current` symlink.
- Produces: verified commit provenance, package import health, and rollback record.

- [ ] Compare the release manifest SHA, release directory name, and `current` target.
- [ ] Run `/home/richard/code/production/quant-platform/current/.venv/bin/python -c 'import portfolio_backtester, strategy_pipeline, quant_execution_engine, research_contracts'` and confirm all four imports resolve from the current release.
- [ ] Run `/home/richard/code/production/quant-platform/current/.venv/bin/python -c 'from pathlib import Path; import portfolio_backtester, strategy_pipeline, quant_execution_engine, research_contracts; root = Path("/home/richard/code/production/quant-platform/current").resolve(); modules = (portfolio_backtester, strategy_pipeline, quant_execution_engine, research_contracts); assert all(root in Path(module.__file__).resolve().parents for module in modules)'` and confirm imports resolve inside the release. Do not invoke service or scheduler entrypoints.
- [ ] Confirm at least the previous two production releases remain available and the old current release remains a rollback target.
- [ ] If any release check fails, use the deployment guide's atomic rollback procedure to restore the previously recorded `current` and verify its manifest.
- [ ] Record promoted SHA, prior SHA, publisher output, smoke-test command, and any retention changes in the final delivery note.
