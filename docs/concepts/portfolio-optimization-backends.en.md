# Portfolio optimization backend boundary

Language: English · [简体中文](portfolio-optimization-backends.md)

`portfolio_backtester` defines a framework-neutral optimization request and result. Backends operate on this contract; third-party solver objects do not leak into caller code.

## Current native backends

The registry implementations include:

- `native.equal_weight`: equal weights across the requested assets.
- `native.hrp`: the existing hierarchical risk parity implementation, projected into requested long-only weight bounds.
- `native.inverse_vol`: inverse recent-volatility preferences, projected into the requested bounds. The default lookback is 252 observations and the default exponent is `0.5`.
- `native.qp_min_variance`: a native minimum-variance QP using SciPy SLSQP, with optional linear exposure bounds and penalties toward anchor or previous weights.

These are reusable portfolio mechanisms. They do not assign strategy-specific meaning to scores, sectors, styles, or other exposure vectors.

## Request contract

`PortfolioOptimizationRequest` carries a return matrix and optional expected returns, previous weights, benchmark weights, anchor weights, covariance matrix, and `LinearExposureConstraint` values. It also carries long-only weight bounds and a covariance-shrinkage parameter.

Asset identities must match across request inputs. Covariance must be finite, symmetric, and ordered to match the return columns. Linear constraints name an exposure vector and may define a lower bound, an upper bound, or both. The current native request contract requires `long_only=True`.

The request keeps common caller inputs available even when a particular baseline does not use them. Backend output still must honor the requested asset set and weight rules.

## Results and validation

`PortfolioOptimizationResult` contains the backend name, normalized weights, JSON-compatible diagnostics, and schema version `portfolio_optimization_result.v1`. Validation checks asset identity, finite weights, a sum of 1, long-only behavior, requested per-asset bounds, and serializable diagnostics.

For `native.qp_min_variance`, `diagnostics.constraint_residuals` records signed slack by constraint name. A lower bound uses the constraint name; an upper bound uses `<name>.upper`. Negative residuals indicate a violated bound. If the solver fails, equal weights are used only when that fallback satisfies the requested bounds; otherwise the call raises an error listing the violated bounds. The result schema remains unchanged.

The contract does not report equality-constraint rank or solution uniqueness. Rank analysis alone would not establish uniqueness once the objective, box bounds, and exposure constraints interact.

## Adding a backend

Keep adapters behind the common request/result contract. A new backend should record its solver and version, pass fixed scenario tests, return validated weights and diagnostics, and leave the native backends usable when an optional dependency is unavailable. No third-party optimizer adapter is currently registered in this module.
