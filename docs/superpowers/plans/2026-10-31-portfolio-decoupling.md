# Portfolio decoupling implementation plan

> **For agentic workers:** Use superpowers:executing-plans; independent SDK and runtime changes are delegated with distinct repository ownership.

**Goal:** Remove the historical directory and new-code dependency on portfolio_backtester while preserving economic behavior and a bounded compatibility surface.

**Architecture:** Keep one Python implementation under a platform owner, neutral platform contracts, explicit public owner facades, and a separate stdlib engine SDK. Legacy algorithms remain available through named compatibility entry points.

**Tech Stack:** Python 3.12+, setuptools/uv, pandas canonical results, Rust/Nautilus engine via pinned CLI.

**Spec:** `docs/superpowers/specs/2026-10-31-portfolio-decoupling-design.md`.

## Global constraints

- Preserve old wire schemas, request hashes and financial behavior.
- No research parameters or private consumer source inventories in public artifacts.
- Outputs and environments outside repositories; each repository has its own task branch.
- No new matching/accounting implementation; unsupported markets retain Python.

## Review focus

- Deep imports and monkeypatches must reference identical implementation modules.
- New contracts and SDK must not import the old simulator transitively.
- Built wheels must contain every facade and compatibility module.
- Lean runtime must neither install nor import platform for Rust jobs.
- Consumer provider pins must reference merged, jointly tested revisions.

## Tasks

- [ ] Inventory module ownership, old import paths and downstream direct imports; record public categories and private caller details separately.
- [ ] Move source layout and add neutral ledger/contracts, explicit owner facades and old import aliases. Test red-to-green isolation, identity and wheel installation.
- [ ] Replace platform subprocess/validation duplication with merged engine SDK and retain canonical mapping only.
- [ ] Migrate platform orchestration and research source callers; freeze old compatibility imports with a ratchet. Preserve legacy economic cases and read paths.
- [ ] Remove mandatory runtime platform dependency; validate lean/full compatibility and document installation modes.
- [ ] Required checks and independent reviews; merge providers before consumers, archive revisions and clean task resources.
