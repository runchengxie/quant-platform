# 因子风险模型实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：**增加通过 PIT 安全检查的因子协方差和特质风险估计，并输出平台原生 pandas 结果。

**架构：**明确因子构建过程。风险模型原语消费预先计算的暴露、因子收益和特质收益，拒绝未来观测，并在不导入组合代码的情况下计算 `X F X' + D`。

**技术栈：**Python 3.12、pandas、NumPy、pytest。

**规范：**`docs/superpowers/specs/2026-09-02-factor-risk-model-design.md`

## 全局约束

- Do not import `portfolio_backtester` or strategy-pipeline.
- All historical rows must be at or before `as_of`.
- No proprietary provider object or data fetcher is introduced.
- Risk-model and optimizer evidence remain separate.

---

### Task 1: Define risk-model tests

**Files:**
- Create: `tests/test_risk_model.py`

- [x] Add tests for projected covariance, positive specific risk, future-data rejection, factor mismatch, and covariance shrinkage.
- [ ] Run `scripts/dev/run_tests.sh` or `uv run --extra dev pytest tests/test_risk_model.py -q` and confirm RED before implementation.

### Task 2: Implement and export the risk model

**Files:**
- Create: `src/alpha_research/risk_model.py`
- Modify: `src/alpha_research/__init__.py`
- Modify: `tests/test_package_smoke.py`

- [x] Implement `FactorRiskModelEstimate` and `build_factor_risk_model()`.
- [x] Enforce finite data, exact factor/asset identity, explicit `as_of`, minimum observations, and optional diagonal shrinkage.
- [x] Export the API and register the owned module in smoke tests.
- [ ] Run `uv run --extra dev pytest tests/test_risk_model.py tests/test_package_smoke.py -q`.

### Task 3: Document and verify

**Files:**
- Create: `docs/concepts/factor-risk-model.md`

- [x] Document ownership, model equation, PIT behavior, and future integration.
- [ ] Run lint, format, typecheck, full tests, and maintainability gates using `scripts/dev/run_tests.sh`.
