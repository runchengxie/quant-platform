# Quantity locks implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline.

**Goal:** Preserve restricted shares while unrelated orders continue.
**Architecture:** Public immutable notices drive owner cancellation, sizing and fill guards; session owns scheduling and checkpoint bindings.
**Tech Stack:** Python, pandas, pytest, existing minute matcher.
**Spec:** `docs/superpowers/specs/2026-11-08-quantity-locks-design.md`

## Global constraints

No private data, strategy parameters, duplicated matcher or corporate actions.
Inclusive nanosecond UTC clocks; no retroactive effect before receipt.

## Review focus

Partial fills, end-time bars, overlaps, delayed acknowledgements and recovery
must preserve holdings without silently cancelling other securities.

## Task 1: Implement and verify owner locks

- [x] Add failing synthetic integration tests for price changes, other-symbol fills, partial cancellation, receipt timing, overlaps and every-boundary recovery.
- [x] Run the tests and confirm the missing notice API fails.
- [x] Add `backtest/quantity_locks.py`; integrate `MinuteSession` and `_MinuteSimulation` guards and read-only decision state.
- [x] Run targeted tests, Ruff, format, ty and full pytest with locked dependencies.
- [x] Review the branch independently, fix important findings, commit and merge against current main.
