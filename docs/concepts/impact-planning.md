# Impact-aware rolling planning

Language: English · [简体中文](impact-planning.zh-CN.md)

Use `quant_platform.portfolio.impact_planning.plan_with_impact` to form a continuous,
long-only finite-horizon plan with diagonal transient impact. Execute only the
first action after the execution owner checks quantities, fees, prices and timing.
Then replan from actual delivered holdings, available cash and impact state.
Existing `portfolio.multiperiod.plan_trades` defaults are unchanged.

The supported problem is a convex QP with conservative affine cash limits.
It does not optimize over the exact economic cash-feasible set. Exact execution
cash is quadratic in trades; treating those constraints as affine would be wrong.
The plan separately reports and checks economic cash and its conservative lower
bound. Capacity may therefore make an economically affordable trade unavailable.

## Request and objective

`ImpactPlanningRequest` uses raw shares and CNY (`units="raw_shares_CNY"`):

- `initial_holdings`, `unaffected_prices`, `initial_transient`, `transient` and
  `decay_seconds` have shape `(N,)`. Prices are fixed positive unaffected marks.
  Displacement is CNY/share (price units), impact coefficients are CNY/share²,
  and decay is strictly positive elapsed seconds, as in
  `LinearImpact`'s `linear-impact.v1` convention. Initial displacement is signed
  and already advanced to `decision_ns`; permanent impact is zero.
- `expected_returns` and nonnegative finite `capacity` have shape `(H,N)`;
  `covariances` has shape `(H,N,N)` and contains symmetric PSD return covariances.
  Symmetry/eigenvalue roundoff within `1e-12` is symmetrized/projected onto PSD.
  `step_seconds` contains `H-1` nonnegative gaps. First action is at elapsed zero;
  equal-clock steps are allowed. Expected returns reward post-trade holdings for
  each step and are not spendable cash.
- `initial_cash`, `reserved_cash` and `risk_aversion` are finite and nonnegative.
  Reservations cannot exceed initial cash. `locked_holdings` is an optional
  `(N,)` floor no greater than initial inventory. Zero capacity locks a step/name.
- `fee_per_share` and `spread_per_share` are nonnegative fixed CNY/share scalars
  or `(N,)` arrays. Spread shifts execution price by trade sign; fees debit cash
  once. Nonzero `fee_rate`, `minimum_fee`, `quantity_step` or `permanent` are
  explicitly unsupported. Integral lots and execution-notional fees need another
  owner-supported decision/recheck process; they are not silently approximated.
- `decision_ns`, `forecast_available_ns`, `risk_available_ns` and
  `state_available_ns` are integer UTC nanoseconds. No availability clock may be
  after the decision. These checks do not authenticate source data or validate
  model fitting history; callers retain those records. All arrays share one
  caller-maintained name order. Do not mutate input arrays during invocation.

Let `q[t]` be signed shares, `h[t] = h[0-] + sum(q[:t+1])`, prices `p`,
initial decision NAV `V = initial_cash + p @ h[0-]`, and elapsed times `s[t]`.
For each name, the pre-fill transient state and execution displacement are

```text
d[t] = exp(-s[t]/tau)*d[0-] + k*sum(exp(-(s[t]-s[u])/tau)*q[u], u<t)
offset[t] = d[t] + k*q[t]/2
state_after[t] = d[t] + k*q[t]
```

The declared objective, returned in CNY, is

```text
sum_t (risk_aversion/(2*V) * (p*h[t])' Sigma[t] (p*h[t])
       - alpha[t]' (p*h[t])
       + q[t]' offset[t] + (fee+spread)' abs(q[t]))
```

The transient quadratic kernel is `k*exp(-abs(s[t]-s[u])/tau)` per name,
which is PSD. Risk is PSD; absolute linear costs use auxiliary variables.
The implementation validates the assembled Hessian. The solve uses NAV-normalized
notional variables for conditioning, analytic gradients and SLSQP; solver success
is not an independent certificate of numerical global optimality. No terminal
liquidation or residual-mark cash is assumed. An initial signed transient state
can benefit an offsetting trade; a zero-state closed round trip at constant
unaffected prices cannot create impact profit.

## Affine cash envelope and execution checks

From capacities `c[t]`, define the nonnegative price displacement bound

```text
B[t] = abs(exp(-s[t]/tau)*d[0-]) + k*c[t]/2
       + k*sum(exp(-(s[t]-s[u])/tau)*c[u], u<t)
cash_lower[t] = initial_cash - sum(p' q[u] + (B[u]+fee+spread)' abs(q[u]), u<=t)
```

The QP enforces `cash_lower[t] >= reserved_cash` using the absolute-value
auxiliary variables; all its constraints are affine or bounds. It rejects
capacity/state combinations with `B[t]+spread >= p`, which could allow nonpositive
execution prices. This restriction and the cash envelope are intentionally
conservative. Cash is checked at each step's net settlement; execute sells before
buys if using their proceeds within a step. Exchange settlement, pending-order
locks and changing actual prices still require the execution owner's checks.

The returned trades are independently propagated through `LinearImpact`, with
half the own increment in fill price. Cash subtracts signed fill notional plus
fixed fees exactly once; impact is never an additional fee. `ImpactPlan` returns
trades, first action, holdings, pre/post transient states, execution prices,
economic cash, affine cash lower bounds, objective, solver status/message and
named residuals. Residuals are dimensionless using decision NAV/notional and must
not exceed `1e-7`. Failed solves or independent infeasibility raise `ValueError`.
The report's `request_digest` binds the request snapshot's numerical float64 bytes,
array shapes, exact integer clocks, configuration and versioned model convention
using SHA-256; it is not source authentication. Preserve source bytes/provenance
and the implementation commit alongside it. Unknown provenance remains unknown.

The first action is continuous, not a submitted order. Before releasing it, use
the existing owner's quantity rounding and feasibility checks, and verify fee and
impact conventions and actual elapsed clocks. Later planned quantities are neither
reserved nor completed trades. Restore the owner's state and replan after actual
fills; do not advance live impact state with hypothetical future trades. The
synthetic tests exercise an exactly integral first action through the existing
minute matcher, restore its state, and check single cash charging.

## Reproduction and limits

`tests/test_impact_planning.py` includes independent hand solutions, capacity and
alpha sensitivity, cash reservations, locked inventory, exact request binding,
owner matching and restoration, and failure rejection. It checks share-unit and
currency scaling, decaying round trips, and same-clock half-own-increment slicing.
Slicing invariance concerns economic impact cost, not identical conservative cash
envelopes under different capacity partitions. Inputs are synthetic, uncalibrated
mechanics, not market impact estimates or evidence of real-market optimality.
