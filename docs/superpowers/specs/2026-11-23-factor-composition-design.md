# Configurable factor composition

Build a public, strategy-independent composition API in Platform and a private experiment consumer in Research. The user requested the supplied architecture and all proposed research directions; implementation proceeds inline without another design round.

## Boundaries and alternatives

A formula-only extension cannot express fitted history or experiment governance. A Research-only implementation would duplicate reusable algorithms. Use a typed public composition contract with a separate private experiment contract. Preserve existing FactorSpec and dynamic ensemble APIs; do not merge their distinct governance semantics.

## Contract

`compose_factors(frame, spec, labels=None, label_available_at=None)` accepts a unique `(date, symbol)` MultiIndex and registered input aliases with explicit factor versions and signs. Inputs are already point-in-time aligned by the caller. Per-date normalization and explicit missing policies precede composition. Results contain score, transformed inputs, effective weights, fit audit and canonical configuration fingerprint. Results never imply data availability was independently certified.

Support equal/weighted/rank, hierarchical, residualized, interaction with main effects, conditional weights, rolling IC/ICIR and regularized covariance weights, PCA, Ridge, PLS and optional LightGBM. Model/IC training uses only rows with feature time and label availability strictly before prediction time, rolling feature-date windows, and an explicit minimum history; insufficient history yields missing scores, not optimistic fallback. IC selection uses complete matured cross-sections. Residualization uses an intercept and explicit direction; rank-deficient exposures fail closed. PCA uses historical training and deterministic sign orientation, not forward returns.

## Research and evidence

Research owns hypothesis, common universe/horizon/cost assumptions, data version, source revision, chronological development/OOS boundaries and holdout governance. Run methods on the same panel, reuse Platform factor diagnostics, compare on a shared scored sample, register trials and export private evidence with exact configuration and input digest. An evaluated holdout is recorded as viewed. Evaluation is predictive evidence, not an executable portfolio backtest or promotion approval. Runtime, public observatory and intelligence consumers remain unchanged until an approved public evidence contract exists; never export private formulas automatically.

## Validation

Hand-calculated score fixtures; missing/constant/tied/nonfinite inputs; malformed or unknown configuration; residual orthogonality; hierarchical group balance; interaction main effects; chronological prefix invariance; unavailable labels and equal-time exclusion; positive IC handling, regularization and weight turnover; historical PCA/model fits; synthetic nonlinear LightGBM integration when installed; Research registry replay and common-sample diagnostics. Run required repository checks and record actual commands, revisions and limitations.
