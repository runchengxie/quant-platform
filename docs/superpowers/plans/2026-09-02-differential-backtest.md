# 差异回测实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**目标：**比较两个规范后端的结果，输出定位明确、机器可读的差异，为后续 RQAlpha 差异证据提供基础。

**规范：**`docs/superpowers/specs/2026-09-02-differential-backtest-design.md`

- [x] Add focused tests for position/NAV localization, identical results, and capability differences.
- [ ] Run the focused test and confirm RED before implementation.
- [x] Implement `DifferentialBacktestReport` and `compare_backtest_results()`.
- [x] Document the RQAlpha/future-adapter role and the current order/fill matching limitation.
- [ ] Run `uv run --extra dev pytest tests/test_differential_backtest.py -q`.
- [ ] Run repository lint, format, typecheck, full test, and maintainability gates.
