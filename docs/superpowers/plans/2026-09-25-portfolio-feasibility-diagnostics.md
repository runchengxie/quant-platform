# Portfolio Feasibility Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make existing portfolio constraint feasibility and fallback behavior directly testable, and add only the smallest compatible diagnostic proven necessary by the audit.

**Architecture:** Keep the framework-neutral request and result boundary in `portfolio_backtester.optimization`. Test bounds, exposure constraints, QP result residuals, and fallback behavior. Any new result diagnostics remain JSON-safe and preserve the existing result schema unless a separate approved design changes it.

**Tech Stack:** Python, pandas, NumPy, SciPy SLSQP, pytest.

**Spec:** `docs/superpowers/specs/2026-09-25-quality-modularization-and-production-design.md`

**实施记录（2026-09-25）：**已由 [PR #48](https://github.com/runchengxie/quant-platform/pull/48) 完成。该 PR 补充约束边界、冲突暴露、等权回退和 JSON 兼容测试，并记录了为何不把等式秩或自由度作为最优解唯一性的结论，也未增加公开诊断字段。矩阵秩示例原计划作为探索测试，评估后没有保留为接口或测试承诺。

## Global Constraints

- Use a dedicated worktree and PR based on latest `origin/main`.
- Preserve `PortfolioOptimizationRequest`, `PortfolioOptimizationResult`, and `portfolio_optimization_result.v1` compatibility.
- Keep strategy-specific semantics outside the optimizer.
- Do not add a dependency on solver-private result types.
- Do not add near-optimal-set search or a general optimization stability service in this work.

## Review Focus

- Conflicting exposure bounds cannot be reported as a successful optimization.
- An infeasible equal-weight fallback raises instead of returning invalid weights.
- Feasible results satisfy budget, bounds, and all exposure residuals within the current tolerance.
- Rank and nullity diagnostics, if added, use the effective equality system and state numerical tolerance explicitly.
- Diagnostics serialize through the existing JSON-safe validation.

---

### Task 1: Pin current request and QP behavior

**Files:**
- Modify: `tests/test_optimizer_backends.py`
- Source: `packages/portfolio-backtester/src/portfolio_backtester/optimization.py`

**Interfaces:**
- Consumes: `LinearExposureConstraint`, `PortfolioOptimizationRequest`, `QpMinVarianceOptimizerBackend`.
- Produces: regression tests for request-level bound feasibility, solver-level exposure feasibility, fallback, and errors.

- [x] Add tests for feasible min/max weights at the exact simplex boundary and infeasible min/max totals.
- [x] Add a contradictory pair of linear exposure bounds and assert the backend fails safely rather than returning violating weights.
- [x] Force solver failure with the existing monkeypatch pattern and test both feasible and infeasible equal-weight fallback cases.
- [x] Assert every successful result's weights sum to one, respect box bounds, and have nonnegative `constraint_residuals` within tolerance.
- [x] Run `uv run --locked python -m pytest tests/test_optimizer_backends.py -q` and confirm new behavior tests fail only where the current implementation is deficient.

### Task 2: Decide whether the existing diagnostics are sufficient

**Files:**
- Review: `packages/portfolio-backtester/src/portfolio_backtester/optimization.py`
- Review: `docs/concepts/portfolio-optimization-backends.md`
- Modify only if required: the same source and docs files

**Interfaces:**
- Consumes: Task 1 test evidence and current JSON-safe diagnostics contract.
- Produces: either a documented finding that current residual diagnostics are sufficient, or an additive JSON-safe field set with tests.

- [x] Inspect callers of `PortfolioOptimizationResult.diagnostics` with `rg -n 'constraint_residuals|solver_status|PortfolioOptimizationResult' packages tests docs`.
- [x] If callers can identify violated named constraints from `constraint_residuals`, document existing behavior and add no new public field.
- [x] If the failure path discards actionable constraint information, add only a named constraint residual/status mapping using built-in JSON scalar/container types.
- [x] Add tests that serialize the result diagnostics and preserve `portfolio_optimization_result.v1`.
- [x] Run `uv run --locked python -m pytest tests/test_optimizer_backends.py tests/test_contracts.py -q`.

### Task 3: Decide whether equality rank belongs in the public diagnostics

**Files:**
- Test: `tests/test_optimizer_backends.py`
- Documentation: `docs/concepts/portfolio-optimization-backends.md`
- Source only if an additive diagnostic is justified: `packages/portfolio-backtester/src/portfolio_backtester/optimization.py`

**Interfaces:**
- Consumes: the optimizer's linear constraints and asset ordering.
- Produces: a documented decision about equality-rank/nullity reporting, plus tested diagnostics only when callers can use them.

- [x] Review whether equality rank/nullity is needed by current consumers and whether it can establish optimizer uniqueness.
- [x] Keep rank/nullity out of the public result because equality rank alone does not establish uniqueness and no caller requires the diagnostic.
- [x] Document the decision in `docs/concepts/portfolio-optimization-backends.md`; do not retain an unused analysis-only test.
- [x] Run the optimizer tests, Ruff, and strict `ty` for the touched paths.

### Task 4: Verify integration and commit

**Files:**
- Modify only files from Tasks 1–3.

**Interfaces:**
- Consumes: all task outputs.
- Produces: a PR with focused optimizer evidence and compatibility results.

- [x] Run `uv run --locked python -m pytest tests/test_optimizer_backends.py tests/test_contracts.py -q`.
- [x] Run `uv run --locked ruff check packages/portfolio-backtester/src/portfolio_backtester/optimization.py tests/test_optimizer_backends.py`.
- [x] Run `uv run --locked ty check --error-on-warning packages/portfolio-backtester/src/portfolio_backtester/optimization.py tests/test_optimizer_backends.py`.
- [x] Commit tests first and any required additive diagnostic separately.
