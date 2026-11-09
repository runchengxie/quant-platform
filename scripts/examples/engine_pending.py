"""Synthetic pending allocation through the legacy Platform API."""

import pandas as pd

from quant_platform.portfolio.pending_allocation import (
    PendingAllocationState,
    PendingOrder,
    solve_pending_allocation,
)
from quant_platform.portfolio.sparse_signed_optimization import (
    SparseSignedOptimizationRequest,
    SparseSignedOptimizer,
)


def run():
    assets = pd.Index(["a", "b", "c"])
    clock = pd.Timestamp("2026-01-01", tz="UTC")
    decision = pd.Timestamp("2026-01-02", tz="UTC")
    assert isinstance(clock, pd.Timestamp) and isinstance(decision, pd.Timestamp)

    def values(value):
        return pd.Series(value, index=assets, dtype=float)

    loadings = pd.DataFrame({"beta": [2.0, 1.0, 0.0]}, index=assets)
    request = SparseSignedOptimizationRequest(
        expected_returns=values([0.1, -0.1, 0.0]),
        risk_loadings=loadings,
        factor_covariance=pd.DataFrame([[0.02]], index=["beta"], columns=["beta"]),
        specific_variance=values(0.1),
        current_weights=values(0),
        lower_bounds=values(-0.5),
        upper_bounds=values(0.5),
        trade_costs=values(0),
        borrow_costs=values(0),
        holding_costs=values(0),
        factor_loadings=loadings,
        factor_bounds={},
        gross_limit=1.0,
        net_target=0.0,
        risk_aversion=1.0,
        horizon_days=5,
        units="horizon_decimal",
        assumptions="Synthetic assumed costs; no calibrated evidence",
        information_time=clock,
        decision_time=decision,
    )
    state = PendingAllocationState(
        delivered_quantities=pd.Series(0, index=assets),
        raw_prices=values(10),
        quote_times=pd.Series(clock, index=assets),
        nav=1000,
        cash_before_reserves=1000,
        sell_capacity_quantities=pd.Series(100, index=assets),
        new_fee_rates=values(0),
        outstanding_orders=(PendingOrder("buy-a", "a", 4, 10, 1, clock),),
        delivered_at=clock,
        orders_as_of=clock,
        complete_order_snapshot=True,
        assumptions="Fixed raw prices and NAV; no planned sale proceeds",
    )
    result = solve_pending_allocation(
        SparseSignedOptimizer(backend="osqp"), request, state, net_band=(-1, 1)
    )
    assert result.status == "optimal"
    assert result.envelope.reserved_cash == 41
    assert result.envelope.available_cash == 959
    assert result.paper_only and not result.executable
    assert result.base_result is not None
    assert result.new_trade_weights is not None
    assert result.new_trade_weights.equals(result.base_result.weights - request.current_weights)
    return result


if __name__ == "__main__":
    result = run()
    print(
        f"{result.status}: reserved={result.envelope.reserved_cash}, paper_only={result.paper_only}"
    )
