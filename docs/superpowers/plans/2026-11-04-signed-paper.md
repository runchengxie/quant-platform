# Signed Paper Optimizer Implementation Plan

**Goal:** Add a generic bounded signed paper optimizer, independent of execution.
**Architecture:** Public module aliases an internal typed contract and convex QP. A feasibility LP precedes analytic-gradient SLSQP; results expose actual economic quantities and residuals.
**Tech Stack:** Existing pandas, numpy, scipy; no dependency changes.
**Spec:** Parent task: explicit horizon decimal inputs, signed bounds, net target, gross upper bound, factor bounds, transaction/borrow/holding assumptions, point-in-time validation.

## Global Constraints
Paper only, no executable output; synthetic tests only; old optimizer unchanged.

## Review Focus
Reject mismatched and duplicate indices, future information, indefinite covariance, infeasible exposures, and disguised zero exposure.

### Task 1: Contract and solver
- [x] Add failing synthetic behavioral and invalid-input tests in tests/test_signed_optimization.py.
- [x] Run targeted pytest and observe missing module failure.
- [x] Implement SignedOptimizationRequest, SignedOptimizationResult, optimize_signed_paper in internal module with public alias.
- [x] Verify tests; expand adversarial tests if needed.

### Task 2: Documentation and validation
- [x] Add reciprocal English/Chinese scope and limitations documents.
- [ ] Run locked sync, full ruff, full pytest; record exact results.
- [ ] Commit and create PR for root review; do not merge.
