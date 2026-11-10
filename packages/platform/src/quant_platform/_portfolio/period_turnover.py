"""Period-level aggregation for leg returns, costs, and turnover diagnostics."""

from __future__ import annotations

from quant_backtest_core.daily.period_turnover import _merged_names as _merged_names
from quant_backtest_core.daily.period_turnover import _optional_sum as _optional_sum
from quant_backtest_core.daily.period_turnover import (
    period_result_from_leg as period_result_from_leg,
)
from quant_backtest_core.daily.period_turnover import (
    period_result_from_legs as period_result_from_legs,
)

from .types import BacktestLegResult as BacktestLegResult
from .types import BacktestPeriodResult


def period_turnover_fields(
    result: BacktestPeriodResult,
) -> dict[str, float | bool | int | tuple[str, ...] | None]:
    """Return the flat period-output contract for turnover reporting."""

    return {
        "target_name_turnover": result.target_name_turnover,
        "target_entered_names": result.target_entered_names,
        "target_exited_names": result.target_exited_names,
        "target_overlap_names": result.target_overlap_names,
        "target_entered_count": len(result.target_entered_names),
        "target_exited_count": len(result.target_exited_names),
        "target_overlap_count": len(result.target_overlap_names),
        "target_weight_full_l1": result.target_weight_full_l1,
        "target_weight_half_l1": result.target_weight_half_l1,
        "pretrade_demand_buy": result.pretrade_demand_buy,
        "pretrade_demand_sell": result.pretrade_demand_sell,
        "pretrade_demand_full_l1": result.pretrade_demand_full_l1,
        "pretrade_demand_half_l1": result.pretrade_demand_half_l1,
        "modeled_fee_cost": result.fee_cost,
        "modeled_slippage_cost": result.slippage_cost,
        "modeled_total_cost": result.total_cost,
        "executed_buy": result.executed_buy,
        "executed_sell": result.executed_sell,
        "executed_gross": result.executed_gross,
        "executed_full_l1": result.executed_full_l1,
        "executed_half_l1": result.executed_half_l1,
        "executed_cost": result.executed_cost,
        "execution_data_available": result.executed_full_l1 is not None,
        "is_initial_build": result.is_initial_build,
        "target_gross_exposure": result.target_gross_exposure,
        "target_cash_weight": result.target_cash_weight,
        "modeled_gross_exposure": result.modeled_gross_exposure,
        "modeled_cash_weight": result.modeled_cash_weight,
    }
