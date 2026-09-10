# Portfolio Construction P0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `quant-platform` 提供 `native.inverse_vol` 和组合级 no-trade 经济再平衡，在 `quant-research` 以薄适配接入冻结的 w025/w089 recipe。

**Architecture:** 平台继续通过 `PortfolioOptimizationRequest -> PortfolioOptimizerBackend -> PortfolioOptimizationResult` 提供策略无关的公共边界。Inverse-vol 参数放在平台的 `InverseVolConfig`，no-trade 作为独立纯函数；研究仓库只保存 recipe 参数并调用平台 backend，不复制算法。

**Tech Stack:** Python 3.12+, pandas, numpy, pytest, uv, ruff。

**Spec:** `docs/superpowers/specs/2026-09-10-portfolio-construction-p0-design.md`

## Global Constraints

- 保留 `portfolio_backtester` Python 命名空间和既有 optimizer result schema。
- 平台不引入策略参数、真实数据、凭证或私有研究模块。
- w025/w089 只在 `quant-research` 保存为冻结研究 recipe：w025=`252/0.5/1%/3%`，w089=`252/1.0/0.5%/4%`。
- 不把非线性执行成本、QP solver、因子模型和 alpha calibration 纳入本切片。
- 所有代码先写失败测试，确认失败原因后再写最小实现。

---

### Task 1: Add inverse-volatility backend to quant-platform

**Files:**
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/optimization.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/__init__.py`
- Modify: `tests/test_optimizer_backends.py`

**Interfaces:**
- Consumes: `PortfolioOptimizationRequest.returns`, request bounds, `InverseVolConfig`.
- Produces: `InverseVolConfig`, `InverseVolOptimizerBackend`, backend name `native.inverse_vol`.

- [x] **Step 1: Write failing tests for configuration and weighting behavior**

Add tests that construct deterministic returns with one lower-volatility asset and assert the backend gives it a higher weight without bounds; assert configured bounds and sum-to-one; assert diagnostics expose method/configuration. Add tests for invalid lookback, exponent, min_periods, insufficient observations, zero volatility, and single-asset behavior.

- [x] **Step 2: Run the focused tests and verify the expected failure**

Run:

```bash
uv run --locked --extra dev python -m pytest tests/test_optimizer_backends.py -q
```

Expected: collection or assertion failures because `InverseVolConfig` and `InverseVolOptimizerBackend` do not exist yet.

- [x] **Step 3: Implement the smallest production API**

Add a frozen `InverseVolConfig` validating positive integer `lookback`, positive finite `exponent`, and `min_periods` in `[1, lookback]`. Add `InverseVolOptimizerBackend` that uses the last `lookback` rows, checks each asset has at least `min_periods` finite observations, computes `std(ddof=1)`, rejects non-finite or non-positive volatilities, computes `volatility.pow(-exponent)`, and passes those preferences to `_project_weights_to_bounds`. Preserve request asset order and return JSON-safe diagnostics. Return 100% for a single asset after request validation.

Export the new public symbols from both `optimization.py` and the package `__init__.py`.

- [x] **Step 4: Run the focused tests and existing optimizer regression tests**

Run:

```bash
uv run --locked --extra dev python -m pytest tests/test_optimizer_backends.py -q
```

Expected: all optimizer tests pass.

- [x] **Step 5: Commit the provider backend**

```bash
git add packages/portfolio-backtester/src/portfolio_backtester/optimization.py \
  packages/portfolio-backtester/src/portfolio_backtester/__init__.py \
  tests/test_optimizer_backends.py
git commit -m "feat: add inverse volatility optimizer backend"
```

### Task 2: Add economic no-trade rebalancing baseline to quant-platform

**Files:**
- Create: `packages/portfolio-backtester/src/portfolio_backtester/economic_rebalance.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/__init__.py`
- Create: `tests/test_economic_rebalance.py`

**Interfaces:**
- Consumes: target and previous fully-invested long-only `pd.Series`, `min_turnover`.
- Produces: `EconomicRebalanceResult` and `apply_no_trade_band`.

- [x] **Step 1: Write failing tests for no-trade decisions and validation**

Cover below-threshold, exactly-at-threshold, and above-threshold half-L1 turnover; missing previous weights; preservation of asset order and input immutability; mismatched assets, negative/non-finite weights, wrong budget, and invalid threshold.

- [x] **Step 2: Run the focused test file and verify it fails for the missing module**

Run:

```bash
uv run --locked --extra dev python -m pytest tests/test_economic_rebalance.py -q
```

Expected: import failure for the not-yet-created module.

- [x] **Step 3: Implement the pure no-trade function**

Validate both Series are finite, non-negative, same-index, and sum to one within `1e-8`. Validate finite non-negative `min_turnover`. Compute `0.5 * abs(target - previous).sum()`. Return an independent copy of previous when turnover is at or below the threshold, otherwise an independent copy of target. For missing previous, return target with `previous_weights_missing=True`. Include the required diagnostics fields and keep them JSON-compatible.

- [x] **Step 4: Run focused and public-surface tests**

Run:

```bash
uv run --locked --extra dev python -m pytest tests/test_economic_rebalance.py tests/test_package_smoke.py -q
```

Expected: all selected tests pass and package exports are available.

- [x] **Step 5: Commit the provider rebalance primitive**

```bash
git add packages/portfolio-backtester/src/portfolio_backtester/economic_rebalance.py \
  packages/portfolio-backtester/src/portfolio_backtester/__init__.py \
  tests/test_economic_rebalance.py
git commit -m "feat: add no-trade economic rebalance baseline"
```

### Task 3: Add frozen w025/w089 research adapter

**Files:**
- Create: `/home/richard/code/.worktrees/quant-research-portfolio-construction/src/strategy_research/portfolio_construction.py`
- Create: `/home/richard/code/.worktrees/quant-research-portfolio-construction/tests/strategy_research/test_portfolio_construction.py`

**Interfaces:**
- Consumes: published `portfolio_backtester.InverseVolConfig` and `InverseVolOptimizerBackend`.
- Produces: `FROZEN_PORTFOLIO_RECIPES`, `frozen_portfolio_optimizer(name)`.

- [x] **Step 1: Write failing contract tests**

Assert `w025` maps to lookback `252`, exponent `0.5`, bounds `0.01`/`0.03`; `w089` maps to `252`, `1.0`, `0.005`/`0.04`; both return a `native.inverse_vol` backend; unknown names raise `ValueError`; and the adapter source does not contain a second inverse-vol calculation.

- [x] **Step 2: Run the focused tests and verify the expected import failure**

Run:

```bash
uv run --locked --extra dev python -m pytest tests/strategy_research/test_portfolio_construction.py -q
```

Expected: import failure because the adapter does not exist yet.

- [x] **Step 3: Implement the research-owned recipe map and thin factory**

Define an immutable recipe record containing `name`, `config`, `min_weight`, and `max_weight`; define the two frozen recipes as constants; implement `frozen_portfolio_optimizer(name)` by normalizing the name, looking it up, and returning `InverseVolOptimizerBackend(config=recipe.config)`. Keep bounds as backend/request configuration at the call site rather than reimplementing weight construction. Do not import private platform helpers.

- [x] **Step 4: Run the focused research tests**

Run:

```bash
uv run --locked --extra dev python -m pytest tests/strategy_research/test_portfolio_construction.py -q
```

For local provider/consumer validation before the provider release is installed, prepend the provider source path:

```bash
PYTHONPATH=/home/richard/code/.worktrees/quant-platform-portfolio-construction/packages/portfolio-backtester/src:src:. \
  uv run --locked --extra dev python -m pytest tests/strategy_research/test_portfolio_construction.py -q
```

Expected: all adapter contract tests pass against the provider worktree's public package; the committed research code must not contain this path.

- [x] **Step 5: Commit the consumer adapter**

```bash
git add src/strategy_research/portfolio_construction.py \
  tests/strategy_research/test_portfolio_construction.py
git commit -m "feat: expose frozen portfolio weighting recipes"
```

### Task 4: Verify both repositories and prepare handoff

**Files:**
- Modify: `docs/reference/public-api.md` to document new root exports.
- Modify: `docs/superpowers/plans/2026-09-10-portfolio-construction-p0.md` to check completed steps only after evidence.

- [x] **Step 1: Run platform formatting, static checks, and full tests**

From `/home/richard/code/.worktrees/quant-platform-portfolio-construction`, run:

```bash
git diff --check
uv run --locked --extra dev ruff check .
uv run --locked --extra dev python -m pytest tests -q
```

Record exact exit codes and any pre-existing warnings; do not claim success from a partial command.

- [x] **Step 2: Run research formatting, static checks, and relevant tests**

From `/home/richard/code/.worktrees/quant-research-portfolio-construction`, run:

```bash
git diff --check
uv run --locked --extra dev ruff check src/strategy_research/portfolio_construction.py tests/strategy_research/test_portfolio_construction.py
PYTHONPATH=src:. uv run --locked --extra dev python -m pytest tests/strategy_research/test_portfolio_construction.py tests/strategy_research -q
```

- [x] **Step 3: Inspect diffs and branch state**

Run `git diff origin/main...HEAD`, `git status --short --branch`, and confirm only intended files changed in each repository.

- [ ] **Step 4: Push provider branch before consumer branch**

Push `feat/portfolio-construction-p0` from platform and prepare its PR to `main`. Only after the provider commit is available should the research branch be pushed and its PR prepared, keeping the dependency direction explicit.
