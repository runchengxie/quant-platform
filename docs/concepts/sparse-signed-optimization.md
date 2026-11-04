# Sparse factor-risk signed paper optimization

[简体中文](sparse-signed-optimization.zh-CN.md)

Use `quant_platform.portfolio.sparse_signed_optimization` for larger synthetic
signed portfolios whose risk is supplied as `B F B.T + diag(D)`. Install
`quant-platform[sparse]` and explicitly select `SparseSignedOptimizer(backend="osqp")`.
The existing [dense signed API](signed-paper-optimization.md) is unchanged.

`SparseSignedOptimizationRequest` uses the dense signed request's scalar,
asset, cost, constraint-factor, horizon, timestamp and assumption fields. Replace
its `covariance` field with these three inputs:

| Field | Contract |
| --- | --- |
| `risk_loadings` | Asset-by-risk-factor DataFrame B, with unique nonempty string factor names and fewer factors than assets |
| `factor_covariance` | Small symmetric positive semidefinite DataFrame F, with both axes matching B's columns exactly |
| `specific_variance` | Nonnegative finite Series D, matching asset labels and order exactly |

Factor covariance validation is strict: F must be exactly symmetric and its computed
small-matrix eigenvalues must all be nonnegative. No negative-eigenvalue tolerance,
symmetrization or clipping is applied: large risk loadings could amplify even
small discrepancies. Validation, the QP and the variance receipt use this same F.
Callers must supply an already valid factor covariance.

Risk factors and `factor_loadings` used for exposure constraints are independent.
All asset Series and both loading matrices must have the same ordered asset
index. Returns, F, D and costs cover the declared `horizon_days`; units are
`horizon_decimal`. Both clocks must be aware pandas Timestamps and information
must not follow decision time. The caller remains responsible for historical
availability and consistent assumptions.

```python
from quant_platform.portfolio.sparse_signed_optimization import (
    SparseSignedOptimizer,
)

solver = SparseSignedOptimizer(backend="osqp", max_iter=100_000, time_limit=10.0, tolerance=1e-9)
result = solver.solve(request)  # SparseSignedOptimizationRequest
next_result = solver.solve(next_request)
```

The solver minimizes `risk_aversion * variance / 2 - expected_return +
trade_cost + borrow_cost + holding_cost`. The existing `SignedOptimizationResult`
reports actual holdings and actual costs, including absolute NAV turnover without
dividing by two. It always sets `paper_only=True` and `executable=False`.
Gross is an upper bound. Zero exposure remains a valid inactive solution.

The CSC program uses weights, absolute trades, absolute holdings, short holdings,
and risk exposures with an equality `risk_exposure = B.T @ weights`. Its Hessian
contains D and the upper triangle of F; an asset-by-asset covariance is never
created. Storage is proportional to loading nonzeros, asset count, constraint
loading nonzeros and the small factor covariance, rather than asset count squared.

Keep one solver for sequential repeated solves. Values update and OSQP reuses
its primal/dual warm start when labels, constraint names and actual CSC patterns
match. Changes in dimensions, labels, factor-bound names or nonzero patterns
rebuild the solver; zero/nonzero changes can therefore invalidate reuse.
`structure_stats` records setup/update counts, matrix nonzeros, variables and
constraints. It measures structure, not numerical factorization reuse or speed.
Instances are mutable and must not be shared across concurrent solves.

Only OSQP's exact `solved` status is accepted. An independent check recomputes
actual asset bounds, gross, net, constraint factors and every auxiliary/equality
constraint, with a maximum violation of `1e-7`. Iteration limits, time limits,
inaccurate statuses and numerical errors return `numerical_failure` with no
weights or economic score. A primal infeasibility certificate returns
`infeasible`. No solver fallback occurs. At larger asset counts, many small
solver errors can accumulate in gross/net; explicitly request a tighter solver
`tolerance` if the independent check rejects a solution. Multiple optima may
produce different feasible weights: compare the economic objective and
constraint violations when assessing warm/cold equivalence.

Run `PYTHONPATH=packages/platform/src uv run --extra sparse python
scripts/benchmarks/sparse_signed_qp.py` for bounded synthetic 100/500/1000 asset
measurements with three cold/warm repetitions. Redirect its JSON under the
project data directory. It records software/build/thread metadata, CSC nonzeros,
time and independently solved objective differences. These are host-specific
measurements, not a latency or memory guarantee; inputs and outputs stay outside
public source control. The implementation follows the official
[OSQP Python interface](https://osqp.org/docs/interfaces/python.html).
