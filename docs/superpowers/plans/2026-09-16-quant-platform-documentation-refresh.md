# Quant Platform Documentation Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update current project naming, ownership, migration status, and Chinese documentation style across quant-platform without changing stable package or CLI compatibility names.

**Architecture:** Treat repository code, package metadata, and tests as the source of truth. Update source Markdown and test descriptions in place, preserving historical repository names where they identify provenance or compatibility boundaries. Regenerate the documentation site only if the repository provides a reproducible documentation build.

**Tech Stack:** Markdown, Python tests, Ruff, pytest, repository documentation checks.

**Spec:** User-approved chat design on 2026-09-16.

## Global Constraints

- Current repository names use the `quant-*` prefixes confirmed in `/home/richard/code/quant`.
- Historical names remain when they identify legacy sources, package names, CLI names, or provenance records.
- Chinese documentation uses natural Chinese phrasing and punctuation, with inline code preserved where it identifies paths, commands, APIs, or names.
- Do not alter algorithm behavior or public Python namespaces as part of the cleanup. Update machine-facing ownership identifiers only where the current repository map confirms the new `quant-*` name.

---

### Task 1: Inventory naming and documentation sources

**Files:**
- Inspect: `README.md`, `AGENTS.md`, `docs/**/*.md`, `docs/**/*.yml`, `docs/**/*.json`, `tests/**/*.py`, `scripts/**/*.py`

- [x] Identify current repository names, historical names, package names, and CLI names with `rg`.
- [x] Classify each match as current ownership, historical provenance, compatibility identity, or stale wording.
- [x] Record only actionable source files. Exclude generated `site/` output until source edits are complete.

### Task 2: Refresh current ownership and naming documentation

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: relevant files under `docs/`
- Test: documentation entrypoint and link tests

- [x] Replace stale current names with `quant-market-data-platform`, `quant-market-research`, `quant-intel-platform`, and `quant-intel-deploy` according to ownership.
- [x] Mark `research-workspace`, `strategy-pipeline`, `portfolio-backtester`, and `quant-execution-engine` as historical or compatibility names where appropriate.
- [x] Update migration status text to reflect completed repository transfer and remaining compatibility boundaries.
- [x] Simplify Chinese prose, remove redundant negation, reduce semicolons and quotation marks, and normalize Chinese punctuation.

### Task 3: Align tests and development scripts

**Files:**
- Modify: affected `tests/**/*.py`
- Modify: affected `scripts/**/*.py` and test documentation

- [x] Update assertions and explanatory text that describe current repository ownership.
- [x] Preserve machine-facing package, CLI, schema, and provenance identifiers unless the source of truth confirms they changed.
- [x] Run targeted documentation and repository-layout tests.

### Task 4: Verify and hand off

- [x] Run documentation checks, `uv run ruff check .`, and `uv run pytest`.
- [x] Run `git diff --check` and review the complete diff for accidental historical-name changes.
- [x] Commit, push, create a PR, and report the verification results.
