# 信号漂移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**目标：**生成由平台维护的信号群体漂移诊断，后续可以发布为 Dashboard 研究证据。

**规范：**`docs/superpowers/specs/2026-09-02-signal-drift-design.md`

- [x] Add tests for identical, shifted, non-finite-filtered, and constant-reference populations.
- [ ] Run focused tests and confirm RED before implementation.
- [x] Implement `SignalDriftReport` and `summarize_signal_drift()` with PSI, KS, mean shift, and std ratio.
- [x] Document the boundary between drift metrics and lifecycle decisions.
- [ ] Run `uv run --extra dev pytest tests/test_signal_drift.py -q`.
- [ ] Run repository lint, format, typecheck, full test, and maintainability gates.
