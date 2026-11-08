# Execution integrity implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline.

**Goal:** Reconcile real backend fill prefixes and expose pooled capacity and exit wealth semantics.
**Architecture:** Small public analytics over recorded fills and targets; synthetic benchmark uses existing owner/SDK only.
**Tech Stack:** Python, Decimal, pandas, pytest, pinned engine SDK.
**Spec:** `docs/superpowers/specs/2026-11-08-execution-integrity-design.md`

## Global constraints

Synthetic public inputs only; no new matcher or runtime, no intraday Rust account-snapshot claim, no pooled sleeve attribution.

## Review focus

Duplicate fill IDs, simultaneous fills, invalid decimal values, mismatched clocks,
held assets with missing marks, and accounting shares as realized cash require tests.

## Task 1: Public evidence helpers

- [ ] Add failing tests for fill-prefix mismatch detection, complete sleeve schedule validation and noncash exit wealth.
- [ ] Implement public helpers, run focused tests.
- [ ] Add synthetic benchmark against actual pinned Rust binary and public Python minute owner, explicitly retaining IOC divergence.
- [ ] Verify pooled versus isolated capacity with one shared owner and impact state.
- [ ] Run Ruff/format/ty/maintainability and full pytest; request independent review, merge PR and retain exact source evidence.
