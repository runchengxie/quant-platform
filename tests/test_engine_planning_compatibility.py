"""Provider B compatibility: exact owners and the retained research optimizer seam."""

import importlib
from dataclasses import replace
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from test_pending_allocation import observation
from test_sparse_signed_optimization import factor_request

from quant_platform.portfolio import pending_allocation as legacy
from quant_platform.portfolio.sparse_signed_optimization import SparseSignedOptimizer

MODULES = {
    **{
        f"quant_platform.backtest.{name}": f"quant_backtest_core.backtest.{name}"
        for name in (
            "paper_account",
            "account_events",
            "_account_event_types",
            "checkpoints",
            "reconciliation",
        )
    },
    **{
        f"quant_platform.portfolio.{name}": f"quant_backtest_core.planning.{name}"
        for name in (
            "impact_planning",
            "multiperiod",
            "discrete_inventory",
            "discrete_oracle",
            "sleeve_allocation",
        )
    },
}


@pytest.mark.parametrize("old,new", MODULES.items())
def test_provider_b_module_and_value_identity(old, new):
    facade, provider = importlib.import_module(old), importlib.import_module(new)
    assert facade is provider
    for name, value in vars(provider).items():
        if isinstance(value, type) or callable(value):
            assert getattr(facade, name) is value


def test_pending_values_are_core_objects():
    core = importlib.import_module("quant_backtest_core.planning.pending_allocation")
    for name in (
        "PendingOrder",
        "PendingAllocationState",
        "PendingAllocationEnvelope",
        "PendingAllocationResult",
    ):
        assert getattr(legacy, name) is getattr(core, name)


@pytest.mark.parametrize(
    "field", ["factor_covariance", "specific_variance", "trade_costs", "risk_loadings"]
)
@pytest.mark.parametrize("infeasible", [False, True])
def test_legacy_standalone_pending_envelope_rejects_invalid_research_risk(field, infeasible):
    request = factor_request()
    value = getattr(request, field).copy()
    value.iloc[0] = np.nan
    invalid = replace(request, **{field: value})
    state = observation(request, cash_before_reserves=-1 if infeasible else 1000)
    with pytest.raises(ValueError):
        legacy.pending_allocation_envelope(invalid, state, net_band=(-1, 1))


def test_legacy_pending_solve_validates_research_before_infeasible_resources():
    request = factor_request()
    invalid = replace(request, factor_covariance=request.factor_covariance * -1)
    with pytest.raises(ValueError):
        legacy.solve_pending_allocation(
            SparseSignedOptimizer(backend="osqp"),
            invalid,
            observation(request, cash_before_reserves=-1),
            net_band=(-1, 1),
        )


def test_real_optimizer_original_result_request_and_cache_are_preserved():
    from quant_platform.portfolio.engine_pending_adapter import PlatformPendingOptimizer

    core = importlib.import_module("quant_backtest_core.planning.pending_allocation")
    request = factor_request()
    before = request.current_weights.copy()
    state = observation(request)
    optimizer = SparseSignedOptimizer(backend="osqp")
    original_solve = optimizer._solve
    captured = []

    def capture(tightened, *, cash_limit):
        result = original_solve(tightened, cash_limit=cash_limit)
        captured.append((tightened, cash_limit, result))
        return result

    with patch.object(optimizer, "_solve", side_effect=capture):
        old = legacy.solve_pending_allocation(optimizer, request, state, net_band=(-1, 1))
        direct = core.solve_pending_allocation(
            PlatformPendingOptimizer(optimizer), request, state, net_band=(-1, 1)
        )
    assert old.status == direct.status == "optimal"
    assert old.base_result is captured[0][2]
    assert direct.base_result is captured[1][2]
    assert old.paper_only is True and old.executable is False
    assert old.base_result.paper_only is True and old.base_result.executable is False
    pd.testing.assert_series_equal(before, request.current_weights)
    pd.testing.assert_series_equal(old.new_trade_weights, direct.new_trade_weights)
    assert captured[0][0] is not request
    assert captured[0][0].risk_loadings is request.risk_loadings
    assert captured[0][0].net_target == request.net_target
    assert captured[0][1][0] == old.envelope.available_cash / state.nav
    np.testing.assert_array_equal(captured[0][1][1], state.new_fee_rates)
    assert optimizer.structure_stats["setups"] == 1
    assert optimizer.structure_stats["updates"] == 1


@pytest.mark.parametrize("status", ["infeasible", "numerical_failure"])
def test_original_failed_optimizer_result_releases_no_targets(status):
    request = factor_request()
    optimizer = SparseSignedOptimizer(backend="osqp")
    original = optimizer.solve(request)
    failure = replace(original, status=status, message="original research failure")
    with patch.object(optimizer, "_solve", return_value=failure):
        result = legacy.solve_pending_allocation(
            optimizer, request, observation(request), net_band=(-1, 1)
        )
    assert result.status == status and result.message == failure.message
    assert result.base_result is None and result.new_trade_weights is None
