# Signed paper portfolio optimization

[简体中文](signed-paper-optimization.zh-CN.md)

Use `quant_platform.portfolio.signed_optimization` for synthetic or paper research
with signed NAV weights. This API is separate from the existing long-only
optimizer. It cannot establish tradability, financing, borrow availability,
locates, account eligibility or execution readiness. Every result has
`paper_only=True` and `executable=False`, including successful optimization.

Construct `SignedOptimizationRequest` with explicit pandas Series for
`expected_returns`, `current_weights`, `lower_bounds`, `upper_bounds`,
`trade_costs`, `borrow_costs`, and `holding_costs`, a square `covariance`
DataFrame, and a `factor_loadings` DataFrame. All asset indices must match in
order, be unique and contain no missing values. All numeric inputs must be
finite. Covariance must be symmetric and positive semidefinite. Missing costs
are rejected; zero costs must be an explicit assumption.

`horizon_days` is a positive integer declaration: expected returns, covariance,
borrow and holding rates all cover that same horizon. `units` must be
`"horizon_decimal"`. Returns and costs are decimals per unit NAV, covariance is
in squared decimal returns, and weights are NAV fractions. Trade costs are
one-time decimal rates per absolute traded NAV. There is no automatic horizon
conversion. The caller is responsible for consistent estimates and documents
these in the required nonempty `assumptions` string. Both timestamps must be timezone-aware `pd.Timestamp` objects (strings and
other timestamp types are rejected); `information_time <= decision_time` attests the latest
information available across all inputs. This check cannot independently
verify historical availability or eliminate estimation bias.

Call `optimize_signed_paper(request)`. The objective minimizes
`risk_aversion / 2 * w.T @ covariance @ w - expected_returns @ w`, plus
`trade_costs @ abs(w-current_weights)`, `borrow_costs @ max(-w,0)`, and
`holding_costs @ abs(w)`. Costs are nonnegative assumptions. Constraints are
asset lower/upper bounds, `sum(w) == net_target`, `sum(abs(w)) <= gross_limit`,
and named `factor_bounds` mapping factor names to finite `(lower, upper)`
exposures. Dollar neutrality does not imply beta neutrality: add a beta
loading column and explicit exposure bound when needed. Gross is an upper
limit, never an exact investment target or minimum. No cash return or cash
account is inferred from signed weights.

The convex program uses absolute-value auxiliary variables, a SciPy HiGHS LP
feasibility start and SLSQP with analytic derivatives. Successful results
include actual weights, gross, net, absolute NAV turnover (without dividing
by two), expected return before costs, variance, each assumed cost, all factor
exposures, and nonnegative constraint violations in `residuals` (tolerance
`1e-7`). `active` means actual gross exceeds `1e-7`; zero exposure is reported
as inactive. `infeasible` means the feasibility LP established inconsistent
constraints; `numerical_failure` covers solver failure or unacceptable
residuals. Both return no weights or economic score, never a fallback
portfolio. SLSQP success is a numerical solution of this convex model, not an
execution approval. The dense solver is intended for small research problems.

These assumptions omit discrete shares, margin mechanics, funding and cash
accounts, market impact, recall risk and point-in-time borrow evidence. Real
execution requires separate evidence, risk checks and execution contracts.
