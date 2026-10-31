"""Lazy public exports; importing a module does not load unrelated simulators."""

from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "EXECUTION_SUMMARY_SCHEMA",
    "PositionBacktestEvaluation",
    "RebalanceTurnoverReport",
    "StrategyRiskReport",
    "TCACalibrationReceipt",
    "TurnoverBreakdown",
    "annualize_turnover",
    "annualized_sharpe_to_periodic",
    "annualized_variance_to_periodic",
    "attribute_delayed_fills",
    "build_comparison_receipt",
    "build_rebalance_turnover_report",
    "calibrate_cost_model",
    "compare_portfolio_returns",
    "deflated_sharpe_ratio",
    "evaluate_position_backtest",
    "execution_summary_frame",
    "expected_max_sharpe",
    "implementation_shortfall_metrics",
    "leg_attribution_frame",
    "name_turnover",
    "probabilistic_sharpe_ratio",
    "probabilistic_sharpe_ratio_from_stats",
    "return_concentration",
    "sharpe_standard_error",
    "strategy_failure_probability",
    "summarize_leg_attribution",
    "summarize_period_returns",
    "summarize_staggered_execution",
    "summarize_strategy_risk",
    "turnover_from_trade_weights",
]

_EXPORTS = {
    "EXECUTION_SUMMARY_SCHEMA": (
        "quant_platform._portfolio.execution_summary",
        "EXECUTION_SUMMARY_SCHEMA",
    ),
    "PositionBacktestEvaluation": (
        "quant_platform._portfolio.position_evaluation",
        "PositionBacktestEvaluation",
    ),
    "RebalanceTurnoverReport": ("quant_platform._portfolio.turnover", "RebalanceTurnoverReport"),
    "StrategyRiskReport": ("quant_platform._portfolio.strategy_risk", "StrategyRiskReport"),
    "TCACalibrationReceipt": ("quant_platform._portfolio.tca_calibration", "TCACalibrationReceipt"),
    "TurnoverBreakdown": ("quant_platform._portfolio.turnover", "TurnoverBreakdown"),
    "annualize_turnover": ("quant_platform._portfolio.turnover", "annualize_turnover"),
    "annualized_sharpe_to_periodic": (
        "quant_platform._portfolio.sharpe_inference",
        "annualized_sharpe_to_periodic",
    ),
    "annualized_variance_to_periodic": (
        "quant_platform._portfolio.sharpe_inference",
        "annualized_variance_to_periodic",
    ),
    "attribute_delayed_fills": (
        "quant_platform._portfolio.execution_diagnostics",
        "attribute_delayed_fills",
    ),
    "build_comparison_receipt": (
        "quant_platform._portfolio.benchmark_comparison",
        "build_comparison_receipt",
    ),
    "build_rebalance_turnover_report": (
        "quant_platform._portfolio.turnover",
        "build_rebalance_turnover_report",
    ),
    "calibrate_cost_model": ("quant_platform._portfolio.tca_calibration", "calibrate_cost_model"),
    "compare_portfolio_returns": (
        "quant_platform._portfolio.benchmark_comparison",
        "compare_portfolio_returns",
    ),
    "deflated_sharpe_ratio": (
        "quant_platform._portfolio.sharpe_inference",
        "deflated_sharpe_ratio",
    ),
    "evaluate_position_backtest": (
        "quant_platform._portfolio.position_evaluation",
        "evaluate_position_backtest",
    ),
    "execution_summary_frame": (
        "quant_platform._portfolio.execution_summary",
        "execution_summary_frame",
    ),
    "expected_max_sharpe": ("quant_platform._portfolio.sharpe_inference", "expected_max_sharpe"),
    "implementation_shortfall_metrics": (
        "quant_platform._portfolio.strategy_risk",
        "implementation_shortfall_metrics",
    ),
    "leg_attribution_frame": ("quant_platform._portfolio.metrics", "leg_attribution_frame"),
    "name_turnover": ("quant_platform._portfolio.turnover", "name_turnover"),
    "probabilistic_sharpe_ratio": (
        "quant_platform._portfolio.strategy_risk",
        "probabilistic_sharpe_ratio",
    ),
    "probabilistic_sharpe_ratio_from_stats": (
        "quant_platform._portfolio.sharpe_inference",
        "probabilistic_sharpe_ratio",
    ),
    "return_concentration": ("quant_platform._portfolio.strategy_risk", "return_concentration"),
    "sharpe_standard_error": (
        "quant_platform._portfolio.sharpe_inference",
        "sharpe_standard_error",
    ),
    "strategy_failure_probability": (
        "quant_platform._portfolio.strategy_risk",
        "strategy_failure_probability",
    ),
    "summarize_leg_attribution": ("quant_platform._portfolio.metrics", "summarize_leg_attribution"),
    "summarize_period_returns": ("quant_platform._portfolio.metrics", "summarize_period_returns"),
    "summarize_staggered_execution": (
        "quant_platform._portfolio.execution_summary",
        "summarize_staggered_execution",
    ),
    "summarize_strategy_risk": (
        "quant_platform._portfolio.strategy_risk",
        "summarize_strategy_risk",
    ),
    "turnover_from_trade_weights": (
        "quant_platform._portfolio.turnover",
        "turnover_from_trade_weights",
    ),
}

if TYPE_CHECKING:
    from quant_platform._portfolio.benchmark_comparison import (
        build_comparison_receipt as build_comparison_receipt,
    )
    from quant_platform._portfolio.benchmark_comparison import (
        compare_portfolio_returns as compare_portfolio_returns,
    )
    from quant_platform._portfolio.execution_diagnostics import (
        attribute_delayed_fills as attribute_delayed_fills,
    )
    from quant_platform._portfolio.execution_summary import (
        EXECUTION_SUMMARY_SCHEMA as EXECUTION_SUMMARY_SCHEMA,
    )
    from quant_platform._portfolio.execution_summary import (
        execution_summary_frame as execution_summary_frame,
    )
    from quant_platform._portfolio.execution_summary import (
        summarize_staggered_execution as summarize_staggered_execution,
    )
    from quant_platform._portfolio.metrics import leg_attribution_frame as leg_attribution_frame
    from quant_platform._portfolio.metrics import (
        summarize_leg_attribution as summarize_leg_attribution,
    )
    from quant_platform._portfolio.metrics import (
        summarize_period_returns as summarize_period_returns,
    )
    from quant_platform._portfolio.position_evaluation import (
        PositionBacktestEvaluation as PositionBacktestEvaluation,
    )
    from quant_platform._portfolio.position_evaluation import (
        evaluate_position_backtest as evaluate_position_backtest,
    )
    from quant_platform._portfolio.sharpe_inference import (
        annualized_sharpe_to_periodic as annualized_sharpe_to_periodic,
    )
    from quant_platform._portfolio.sharpe_inference import (
        annualized_variance_to_periodic as annualized_variance_to_periodic,
    )
    from quant_platform._portfolio.sharpe_inference import (
        deflated_sharpe_ratio as deflated_sharpe_ratio,
    )
    from quant_platform._portfolio.sharpe_inference import (
        expected_max_sharpe as expected_max_sharpe,
    )
    from quant_platform._portfolio.sharpe_inference import (
        probabilistic_sharpe_ratio as probabilistic_sharpe_ratio_from_stats,
    )
    from quant_platform._portfolio.sharpe_inference import (
        sharpe_standard_error as sharpe_standard_error,
    )
    from quant_platform._portfolio.strategy_risk import StrategyRiskReport as StrategyRiskReport
    from quant_platform._portfolio.strategy_risk import (
        implementation_shortfall_metrics as implementation_shortfall_metrics,
    )
    from quant_platform._portfolio.strategy_risk import (
        probabilistic_sharpe_ratio as probabilistic_sharpe_ratio,
    )
    from quant_platform._portfolio.strategy_risk import return_concentration as return_concentration
    from quant_platform._portfolio.strategy_risk import (
        strategy_failure_probability as strategy_failure_probability,
    )
    from quant_platform._portfolio.strategy_risk import (
        summarize_strategy_risk as summarize_strategy_risk,
    )
    from quant_platform._portfolio.tca_calibration import (
        TCACalibrationReceipt as TCACalibrationReceipt,
    )
    from quant_platform._portfolio.tca_calibration import (
        calibrate_cost_model as calibrate_cost_model,
    )
    from quant_platform._portfolio.turnover import (
        RebalanceTurnoverReport as RebalanceTurnoverReport,
    )
    from quant_platform._portfolio.turnover import TurnoverBreakdown as TurnoverBreakdown
    from quant_platform._portfolio.turnover import annualize_turnover as annualize_turnover
    from quant_platform._portfolio.turnover import (
        build_rebalance_turnover_report as build_rebalance_turnover_report,
    )
    from quant_platform._portfolio.turnover import name_turnover as name_turnover
    from quant_platform._portfolio.turnover import (
        turnover_from_trade_weights as turnover_from_trade_weights,
    )


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, symbol = _EXPORTS[name]
    value = getattr(import_module(module), symbol)
    globals()[name] = value
    return value
