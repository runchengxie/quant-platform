# 优化器后端边界实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：**增加由维护方控制的优化器请求和结果边界，并提供原生等权和 HRP 基线。

**架构：**让优化与回测、执行后端保持分离。外部求解器适配器负责 pandas 或平台原生类型之间的转换，第三方对象不得通过公共 API 泄漏。

**技术栈：**Python 3.12、pandas、NumPy、现有 HRP 实现和 pytest。

**规范：**`docs/superpowers/specs/2026-09-02-optimizer-backend-boundary-design.md`

## 全局约束

- No new runtime dependency.
- Existing HRP implementation is reused, not copied.
- New request/result types remain framework-neutral.
- Long-only is the only supported native optimization mode in this PR.

---

### Task 1: Define tests and canonical types

**Files:**
- Create: `tests/test_optimizer_backends.py`
- Create: `src/portfolio_backtester/optimization.py`

- [x] Write tests for equal weight, HRP bounds, registry behavior, asset mismatch, and infeasible bounds.
- [ ] Run `uv run --extra dev pytest tests/test_optimizer_backends.py -q` and confirm RED before implementation.
- [x] Implement request/result validation, registry, equal-weight baseline, and HRP adapter.
- [ ] Run focused tests and confirm PASS.

### Task 2: Publish the owner API

**Files:**
- Modify: `src/portfolio_backtester/__init__.py`
- Modify: `tests/test_package_smoke.py`
- Create: `docs/concepts/portfolio-optimization-backends.md`

- [x] Export the optimizer types and native backends.
- [x] Register the new module and exports in package smoke tests.
- [x] Document external-adapter adoption order.
- [ ] Run `uv run --extra dev pytest tests/test_optimizer_backends.py tests/test_package_smoke.py -q`.

### Task 3: Repository gates

- [ ] Run `scripts/dev/run_tests.sh lint`.
- [ ] Run `scripts/dev/run_tests.sh format`.
- [ ] Run `scripts/dev/run_tests.sh typecheck`.
- [ ] Run `scripts/dev/run_tests.sh all`.
- [ ] Run `scripts/dev/run_tests.sh maintainability` and separate any pre-existing ratchet failure from this change.
