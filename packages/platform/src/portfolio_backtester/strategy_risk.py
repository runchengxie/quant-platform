"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "StrategyRiskReport",
    "_elapsed_years",
    "_empty_shortfall",
    "annotations",
    "asdict",
    "dataclass",
    "implementation_shortfall_metrics",
    "implied_precision",
    "normalized_hhi",
    "probabilistic_sharpe_ratio",
    "probabilistic_sharpe_ratio_from_stats",
    "return_concentration",
    "sqrt",
    "strategy_failure_probability",
    "summarize_strategy_risk",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.strategy_risk import (
        StrategyRiskReport,
        _elapsed_years,
        _empty_shortfall,
        annotations,
        asdict,
        dataclass,
        implementation_shortfall_metrics,
        implied_precision,
        normalized_hhi,
        probabilistic_sharpe_ratio,
        probabilistic_sharpe_ratio_from_stats,
        return_concentration,
        sqrt,
        strategy_failure_probability,
        summarize_strategy_risk,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.strategy_risk")
