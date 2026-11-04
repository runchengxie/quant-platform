# Pending-aware paper allocation

Use `quant_platform.portfolio.pending_allocation` to reserve outstanding orders
before computing additional trades with `SparseSignedOptimizer(backend="osqp")`.
This optional public API preserves the existing sparse request and solver API.
It supplies a conservative, single-period conditional endpoint envelope, using
only delivered holdings, delivered remaining orders and caller-known resources.
All examples and validation use synthetic inputs.

## Target and order semantics

Let `h` be the delivered holdings valued at supplied raw prices divided by positive
NAV. The sparse request's `current_weights` must equal `h`. Replacing it with
assumed filled holdings is rejected. Let `b` be the optimized base target and
`delta = b - h` the NEW trade weights. For each outstanding order `j`, its signed
remaining raw quantity produces `p_j = quantity_j * raw_price_j / NAV` in its
symbol. Each old order has an independent unknown fill fraction `f_j` in `[0, 1]`.
The conditional endpoint follows this identity.

```text
endpoint = b + sum_j(f_j * p_j)
NEW trades = b - h
```

`b` excludes outstanding orders. Neither subtract outstanding orders from it
again nor submit `b` itself as incremental orders. The return field
`new_trade_weights` already contains the additional trades. It remains a paper
weight proposal. It provides no integer-share rounding or order admission.

The envelope is conditional on NEW trades filling completely. It does not
guarantee constraints along intermediate paths or when new orders fill partially.
The caller must choose its own execution/admission policy. The implementation
does not cancel orders, invent fills, optimize a fill schedule or read hidden
`AccountEventAdapter.actual` state.

## Observations and clocks

Construct `PendingAllocationState` with matching asset-indexed Series for
`delivered_quantities`, `raw_prices`, `quote_times`,
`sell_capacity_quantities` and `new_fee_rates`. Supply `nav`,
`cash_before_reserves`, `outstanding_orders`, `delivered_at`, `orders_as_of`,
`complete_order_snapshot=True` and explicit `assumptions`.

The caller attests completeness by including all outstanding orders, including
requested cancellations and fills not yet reported. Each `PendingOrder` records
its identifier, symbol, signed remaining integer quantity, assumed buy reservation
price ceiling, remaining fee budget and observation timestamp. Unknown symbols,
duplicate identifiers, future/naive clocks, incomplete snapshots, mismatched
holdings and nonfinite values are rejected. All observation timestamps must be
at or before the request's information time. `orders_as_of` must equal that time.
Information time must precede or equal decision time, following the sparse API.
These checks cannot discover orders omitted by a caller who incorrectly attests
completeness. There is no automatic quote-age limit. Freshness is a caller policy.

With `AccountEventAdapter`, use `visible` quantities, independent causal raw
quotes, `visible_nav` revalued to the supplied raw prices if necessary, and
delivery-visible `pending` remaining quantities. A hidden fill changes neither
the supplied holdings nor pending quantities until its report is delivered.
Do not use `actual`, `actual_nav`, actual order ledgers or undelivered reports.
Extract only the public delivered snapshot. The allocator does not depend on the
account adapter or create a second matcher.

## Exposure envelope

For any linear load `a`, compute the exact independent-fill increment interval.

```text
L(a) = sum_j min(0, a[symbol_j] * p_j)
U(a) = sum_j max(0, a[symbol_j] * p_j)
```

For requested endpoint interval `[lo, hi]`, constrain `a @ b` to
`[lo - L(a), hi - U(a)]`. Apply this to each constrained factor, individual asset
bounds, and net exposure (`a = 1`). Opposing orders do not cancel. A pending buy
of 0.1 and sell of 0.1 in the same symbol yield net increment `[-0.1, 0.1]`,
not zero. A factor with negative loadings uses the same signed formula.

The sparse request's `net_target` continues to fix base net exposure. The new
required `net_band=(lo, hi)` constrains conditional endpoint net exposure. The
base net must lie in the tightened interval. Exact endpoint neutrality with
independently uncertain signed pending fills is generally infeasible, even when
the signed sum of pending orders is zero. No neutral result is fabricated.

Gross is bounded conservatively by `sum(abs(b)) + sum_j(abs(p_j))`, so the base
QP gross cap is reduced by `sum_j(abs(p_j))`. This triangle bound can reject
feasible offsets. It is sufficient for every old fill corner. It is not an exact
robust gross optimizer. Factor and net intervals are exact for each linear load.

## Cash, sales and locates

`cash_before_reserves` means discretionary delivered cash after restricted cash,
unsettled proceeds and existing short collateral, but before subtracting
outstanding-order reservations. It may include explicitly authorized credit if
the caller's policy permits it. Reserve each old order separately.

```text
old cash reserve = sum_j(max(quantity_j, 0) * max(reserve_price_j, raw_price_j)
                         + fee_budget_j)
remaining cash = cash_before_reserves - old cash reserve
new cash = NAV * sum_i((abs(delta_i) + delta_i) / 2
                       + new_fee_rate_i * abs(delta_i))
```

Fees apply to both buys and sales. Proceeds from pending or new sales do not fund
buys. `new_fee_rates` are explicit proportional fee assumptions, independent of
the sparse request's utility `trade_costs`. New buy cash and fees use the supplied
fixed raw prices. Old `reserve_price` values are assumed buy execution-price
ceilings, with at least raw price reserved. These assumptions provide no
protection against adverse repricing on new orders. Minimum fees and nonlinear
costs need another model. The sparse QP uses its absolute-trade auxiliaries to
impose the aggregate cash inequality. The receipt recomputes cash directly from
returned `delta`. Do not supply cash already reduced by outstanding reservations,
which would reserve them twice. With the event adapter and no extra credit,
`available_cash(info_time) + sum(pending_order["reserved_cash"])` provides the
appropriate basis. Reconcile the caller's reserve price assumptions separately.

Each `sell_capacity_quantities` value is available delivered long inventory plus
confirmed incremental locate units before outstanding sales. Incremental
locates exclude units consumed by existing delivered shorts. For example, ten
delivered short shares with thirteen confirmed total locate units leave three
incremental units. Subtract every old pending sale in full. New
negative trade quantities may not exceed the remainder. A pending buy, new buy
or short cover does not replenish that capacity during this decision. This is
deliberately conservative about sale/cover ordering and avoids reusing locates.
The caller supplies known sellability restrictions. This module cannot establish
borrow access or infer settlement/T+1 eligibility.

## Calling and interpreting the result

```python
from quant_platform.portfolio.pending_allocation import solve_pending_allocation
from quant_platform.portfolio.sparse_signed_optimization import SparseSignedOptimizer

result = solve_pending_allocation(
    SparseSignedOptimizer(backend="osqp"),
    request,  # existing SparseSignedOptimizationRequest; delivered baseline
    observation,  # PendingAllocationState; no hidden actual state
    net_band=(-0.15, 0.15),
)
if result.status == "optimal":
    additional_paper_weights = result.new_trade_weights
    conditional_endpoint_net = result.endpoint_net_bounds
```

`pending_allocation_envelope` exposes tightened bounds and reservations without
solving. `solve_pending_allocation` returns that envelope with a status. On
success, `base_result` retains existing sparse economics and turnover measured
against delivered holdings. `endpoint_net_bounds`, `endpoint_factor_bounds`,
`endpoint_gross_upper` and `new_cash_required` describe the conditional envelope.
The objective values risk/return on the base target. It does not optimize
worst-case economics across old fills. Factor receipt intervals cover constrained
factors. Failures return no base target or additional trades. Invalid observations
raise `ValueError`. Insufficient resources or impossible tightened bounds return
`infeasible`. Solver and residual failures return `numerical_failure`.

Prices and NAV stay fixed over exactly the request's single holding period.
Adverse price moves, NAV changes, new partial-fill paths, margin changes,
corporate actions, financing, locates revoked after the snapshot and multi-period
adaptation are outside this contract. Both result flags remain
`paper_only=True`, `executable=False`.
