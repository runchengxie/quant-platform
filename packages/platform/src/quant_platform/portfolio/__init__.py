"""Lazy public exports; importing a module does not load unrelated simulators."""

from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA",
    "POSITIONS_BY_REBALANCE_CONTRACT",
    "CostBreakdown",
    "EconomicRebalanceResult",
    "EqualWeightOptimizerBackend",
    "GroupCap",
    "HrpConfig",
    "HrpOptimizerBackend",
    "HrpResult",
    "InverseVolConfig",
    "InverseVolOptimizerBackend",
    "LinearExposureConstraint",
    "OptimizerRegistry",
    "PortfolioOptimizationRequest",
    "PortfolioOptimizationResult",
    "PortfolioOptimizerBackend",
    "PortfolioQpConfig",
    "PositionsByRebalanceFrameContract",
    "QpMinVarianceOptimizerBackend",
    "SessionRebalanceSchedule",
    "SizingConfig",
    "StrategySpec",
    "apply_no_trade_band",
    "assert_positions_by_rebalance_frame",
    "average_active_bets",
    "build_sized_weights",
    "build_sizing_receipt",
    "construct_positions_from_strategy",
    "discretize_weights",
    "get_rebalance_events",
    "get_session_interval_rebalance_dates",
    "hierarchical_risk_parity",
    "probability_to_size",
    "rolling_hrp_weights",
    "strategy_from_config",
    "validate_positions_by_rebalance_frame",
]

_EXPORTS = {
    "PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA": (
        "quant_platform._portfolio.optimization",
        "PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA",
    ),
    "POSITIONS_BY_REBALANCE_CONTRACT": (
        "quant_platform._portfolio.contracts",
        "POSITIONS_BY_REBALANCE_CONTRACT",
    ),
    "CostBreakdown": ("quant_platform._portfolio.types", "CostBreakdown"),
    "EconomicRebalanceResult": (
        "quant_platform._portfolio.economic_rebalance",
        "EconomicRebalanceResult",
    ),
    "EqualWeightOptimizerBackend": (
        "quant_platform._portfolio.optimization",
        "EqualWeightOptimizerBackend",
    ),
    "GroupCap": ("quant_platform._portfolio.contracts", "GroupCap"),
    "HrpConfig": ("quant_platform._portfolio.hrp", "HrpConfig"),
    "HrpOptimizerBackend": ("quant_platform._portfolio.optimization", "HrpOptimizerBackend"),
    "HrpResult": ("quant_platform._portfolio.hrp", "HrpResult"),
    "InverseVolConfig": ("quant_platform._portfolio.optimization", "InverseVolConfig"),
    "InverseVolOptimizerBackend": (
        "quant_platform._portfolio.optimization",
        "InverseVolOptimizerBackend",
    ),
    "LinearExposureConstraint": (
        "quant_platform._portfolio.optimization",
        "LinearExposureConstraint",
    ),
    "OptimizerRegistry": ("quant_platform._portfolio.optimization", "OptimizerRegistry"),
    "PortfolioOptimizationRequest": (
        "quant_platform._portfolio.optimization",
        "PortfolioOptimizationRequest",
    ),
    "PortfolioOptimizationResult": (
        "quant_platform._portfolio.optimization",
        "PortfolioOptimizationResult",
    ),
    "PortfolioOptimizerBackend": (
        "quant_platform._portfolio.optimization",
        "PortfolioOptimizerBackend",
    ),
    "PortfolioQpConfig": ("quant_platform._portfolio.optimization", "PortfolioQpConfig"),
    "PositionsByRebalanceFrameContract": (
        "quant_platform._portfolio.contracts",
        "PositionsByRebalanceFrameContract",
    ),
    "QpMinVarianceOptimizerBackend": (
        "quant_platform._portfolio.optimization",
        "QpMinVarianceOptimizerBackend",
    ),
    "SessionRebalanceSchedule": ("quant_platform._portfolio.rebalance", "SessionRebalanceSchedule"),
    "SizingConfig": ("quant_platform._portfolio.bet_sizing", "SizingConfig"),
    "StrategySpec": ("quant_platform._portfolio.contracts", "StrategySpec"),
    "apply_no_trade_band": ("quant_platform._portfolio.economic_rebalance", "apply_no_trade_band"),
    "assert_positions_by_rebalance_frame": (
        "quant_platform._portfolio.contracts",
        "assert_positions_by_rebalance_frame",
    ),
    "average_active_bets": ("quant_platform._portfolio.bet_sizing", "average_active_bets"),
    "build_sized_weights": ("quant_platform._portfolio.bet_sizing", "build_sized_weights"),
    "build_sizing_receipt": ("quant_platform._portfolio.bet_sizing", "build_sizing_receipt"),
    "construct_positions_from_strategy": (
        "quant_platform._portfolio.strategy",
        "construct_positions_from_strategy",
    ),
    "discretize_weights": ("quant_platform._portfolio.bet_sizing", "discretize_weights"),
    "get_rebalance_events": ("quant_platform._portfolio.rebalance", "get_rebalance_events"),
    "get_session_interval_rebalance_dates": (
        "quant_platform._portfolio.rebalance",
        "get_session_interval_rebalance_dates",
    ),
    "hierarchical_risk_parity": ("quant_platform._portfolio.hrp", "hierarchical_risk_parity"),
    "probability_to_size": ("quant_platform._portfolio.bet_sizing", "probability_to_size"),
    "rolling_hrp_weights": ("quant_platform._portfolio.hrp", "rolling_hrp_weights"),
    "strategy_from_config": ("quant_platform._portfolio.strategy", "strategy_from_config"),
    "validate_positions_by_rebalance_frame": (
        "quant_platform._portfolio.contracts",
        "validate_positions_by_rebalance_frame",
    ),
}

if TYPE_CHECKING:
    from quant_platform._portfolio.bet_sizing import SizingConfig as SizingConfig
    from quant_platform._portfolio.bet_sizing import average_active_bets as average_active_bets
    from quant_platform._portfolio.bet_sizing import build_sized_weights as build_sized_weights
    from quant_platform._portfolio.bet_sizing import build_sizing_receipt as build_sizing_receipt
    from quant_platform._portfolio.bet_sizing import discretize_weights as discretize_weights
    from quant_platform._portfolio.bet_sizing import probability_to_size as probability_to_size
    from quant_platform._portfolio.contracts import (
        POSITIONS_BY_REBALANCE_CONTRACT as POSITIONS_BY_REBALANCE_CONTRACT,
    )
    from quant_platform._portfolio.contracts import GroupCap as GroupCap
    from quant_platform._portfolio.contracts import (
        PositionsByRebalanceFrameContract as PositionsByRebalanceFrameContract,
    )
    from quant_platform._portfolio.contracts import StrategySpec as StrategySpec
    from quant_platform._portfolio.contracts import (
        assert_positions_by_rebalance_frame as assert_positions_by_rebalance_frame,
    )
    from quant_platform._portfolio.contracts import (
        validate_positions_by_rebalance_frame as validate_positions_by_rebalance_frame,
    )
    from quant_platform._portfolio.economic_rebalance import (
        EconomicRebalanceResult as EconomicRebalanceResult,
    )
    from quant_platform._portfolio.economic_rebalance import (
        apply_no_trade_band as apply_no_trade_band,
    )
    from quant_platform._portfolio.hrp import HrpConfig as HrpConfig
    from quant_platform._portfolio.hrp import HrpResult as HrpResult
    from quant_platform._portfolio.hrp import hierarchical_risk_parity as hierarchical_risk_parity
    from quant_platform._portfolio.hrp import rolling_hrp_weights as rolling_hrp_weights
    from quant_platform._portfolio.optimization import (
        PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA as PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA,
    )
    from quant_platform._portfolio.optimization import (
        EqualWeightOptimizerBackend as EqualWeightOptimizerBackend,
    )
    from quant_platform._portfolio.optimization import HrpOptimizerBackend as HrpOptimizerBackend
    from quant_platform._portfolio.optimization import InverseVolConfig as InverseVolConfig
    from quant_platform._portfolio.optimization import (
        InverseVolOptimizerBackend as InverseVolOptimizerBackend,
    )
    from quant_platform._portfolio.optimization import (
        LinearExposureConstraint as LinearExposureConstraint,
    )
    from quant_platform._portfolio.optimization import OptimizerRegistry as OptimizerRegistry
    from quant_platform._portfolio.optimization import (
        PortfolioOptimizationRequest as PortfolioOptimizationRequest,
    )
    from quant_platform._portfolio.optimization import (
        PortfolioOptimizationResult as PortfolioOptimizationResult,
    )
    from quant_platform._portfolio.optimization import (
        PortfolioOptimizerBackend as PortfolioOptimizerBackend,
    )
    from quant_platform._portfolio.optimization import PortfolioQpConfig as PortfolioQpConfig
    from quant_platform._portfolio.optimization import (
        QpMinVarianceOptimizerBackend as QpMinVarianceOptimizerBackend,
    )
    from quant_platform._portfolio.rebalance import (
        SessionRebalanceSchedule as SessionRebalanceSchedule,
    )
    from quant_platform._portfolio.rebalance import get_rebalance_events as get_rebalance_events
    from quant_platform._portfolio.rebalance import (
        get_session_interval_rebalance_dates as get_session_interval_rebalance_dates,
    )
    from quant_platform._portfolio.strategy import (
        construct_positions_from_strategy as construct_positions_from_strategy,
    )
    from quant_platform._portfolio.strategy import strategy_from_config as strategy_from_config
    from quant_platform._portfolio.types import CostBreakdown as CostBreakdown


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, symbol = _EXPORTS[name]
    value = getattr(import_module(module), symbol)
    globals()[name] = value
    return value
