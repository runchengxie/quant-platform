"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BacktestLegResult",
    "BacktestPositionState",
    "CostModel",
    "Literal",
    "RebalanceTurnoverReport",
    "SlippageModel",
    "TargetWeightPolicy",
    "_TargetWeightsAndExit",
    "_build_backtest_leg_result",
    "_build_leg_turnover_report",
    "_build_target_weights_and_exit",
    "_compute_trade_summary",
    "_drift_previous_weights",
    "_next_position_state",
    "annotations",
    "build_position_weights",
    "build_rebalance_turnover_report",
    "cast",
    "clean_position_weights",
    "dataclass",
    "limit_weight_turnover",
    "slippage_pricing_row",
    "turnover_from_trade_weights",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.leg_helpers import (
        BacktestLegResult,
        BacktestPositionState,
        CostModel,
        Literal,
        RebalanceTurnoverReport,
        SlippageModel,
        TargetWeightPolicy,
        _build_backtest_leg_result,
        _build_leg_turnover_report,
        _build_target_weights_and_exit,
        _compute_trade_summary,
        _drift_previous_weights,
        _next_position_state,
        _TargetWeightsAndExit,
        annotations,
        build_position_weights,
        build_rebalance_turnover_report,
        cast,
        clean_position_weights,
        dataclass,
        limit_weight_turnover,
        slippage_pricing_row,
        turnover_from_trade_weights,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.leg_helpers")
