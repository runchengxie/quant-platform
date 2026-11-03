"""Public synthetic checks; these parameters are not market calibration."""
import pytest

from quant_platform.backtest.impact_scenarios import linear_impact_scenario
from quant_platform.portfolio.discrete_oracle import enumerate_lot_portfolios


def test_permanent_round_trip_conserves_quantity_without_manipulation_profit():
    result = linear_impact_scenario([4, -1, -3], unaffected_price=100, permanent=0.5,
                                    temporary=0.1, fee_per_share=0.02)
    assert result.final_inventory == 0
    assert result.final_displacement == 0
    assert result.cash_change == pytest.approx(-2.76)
    assert sum(fill.quantity for fill in result.fills) == 0
    assert result.fills[0].execution_price == pytest.approx(101.4)


def test_splitting_preserves_linear_permanent_integral():
    first = linear_impact_scenario([4], unaffected_price=100, permanent=0.5)
    split = linear_impact_scenario([1, 3], unaffected_price=100, permanent=0.5)
    assert first.cash_change == split.cash_change == -404


@pytest.mark.parametrize('kwargs', [{'permanent': -1}, {'temporary': float('nan')},
                                    {'fee_per_share': -1}, {'unaffected_price': 0}])
def test_impact_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        linear_impact_scenario([1], **({'unaffected_price': 100} | kwargs))


def test_discrete_oracle_exposes_rounding_gap_and_budget():
    result = enumerate_lot_portfolios(prices=[6, 4], target_quantities=[1.5, 1.5],
        max_lots=[3, 3], lot_sizes=[1, 1], cash_budget=14, minimum_commission=1,
        candidate_quantities=[2, 1])
    assert result.status == 'optimal_exhaustive'
    assert result.quantities == (1, 1)
    assert result.spent == 12
    assert result.objective == 0.5
    assert result.candidate_status == 'infeasible'
    assert result.candidate_gap is None
    assert result.evaluated == 16


def test_feasible_heuristic_has_reported_suboptimal_gap():
    result = enumerate_lot_portfolios(prices=[6, 4], target_quantities=[1.5, 1.5],
        max_lots=[3, 3], lot_sizes=[1, 1], cash_budget=14, minimum_commission=1,
        candidate_quantities=[0, 2])
    assert result.candidate_status == 'feasible'
    assert result.candidate_gap == 2


def test_search_limit_is_rejection_not_false_optimality():
    result = enumerate_lot_portfolios(prices=[1], target_quantities=[1], max_lots=[100],
        lot_sizes=[1], cash_budget=10, max_states=10)
    assert result.status == 'search_limit'
    assert result.quantities is None
    assert result.evaluated == 0


def test_existing_continuous_qp_matches_analytic_risk_and_quadratic_turnover_baseline():
    import pandas as pd

    from quant_platform.portfolio.optimization import (
        PortfolioOptimizationRequest,
        PortfolioQpConfig,
        QpMinVarianceOptimizerBackend,
    )

    # Objective .5*(wA**2 + 4*wB**2) + .5*||w - (.5,.5)||**2.
    # On wB=1-wA, derivative 7*wA-5 = 0.
    request = PortfolioOptimizationRequest(
        returns=pd.DataFrame({'A': [0.01, -0.01], 'B': [0.02, -0.02]}),
        covariance=pd.DataFrame([[1., 0.], [0., 4.]], index=['A', 'B'], columns=['A', 'B']),
        previous_weights=pd.Series({'A': .5, 'B': .5}),
    )
    result = QpMinVarianceOptimizerBackend(PortfolioQpConfig(previous_penalty=.5)).run(request)
    assert result.weights['A'] == pytest.approx(5 / 7, abs=1e-6)
    assert result.weights['B'] == pytest.approx(2 / 7, abs=1e-6)


@pytest.mark.parametrize('kwargs', [{'max_lots': [-1]}, {'lot_sizes': [0]},
                                    {'cash_budget': -1}, {'max_states': 0},
                                    {'minimum_commission': float('inf')}])
def test_lot_oracle_rejects_invalid_contract(kwargs):
    base = {'prices': [1], 'target_quantities': [1], 'max_lots': [2],
            'lot_sizes': [1], 'cash_budget': 3}
    with pytest.raises(ValueError):
        enumerate_lot_portfolios(**(base | kwargs))


def test_decimal_cash_boundary_preserves_feasible_exact_target():
    result = enumerate_lot_portfolios(prices=[0.1, 0.2], target_quantities=[1, 1],
        max_lots=[1, 1], lot_sizes=[1, 1], cash_budget=0.3)
    assert result.quantities == (1, 1)
    assert result.spent == 0.3
    assert result.objective == 0


@pytest.mark.parametrize('path', [[1, -1], [-2, 1, 1], [1, 3, -2, -2], [0, 2, -2]])
def test_permanent_only_round_trips_have_zero_cash_change(path):
    result = linear_impact_scenario(path, unaffected_price=100, permanent=.5)
    assert result.cash_change == pytest.approx(0)
    assert result.final_inventory == 0
