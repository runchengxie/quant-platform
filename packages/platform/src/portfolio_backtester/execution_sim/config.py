"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "SELL_UNTIL_NEXT_REBALANCE",
    "Any",
    "ExecutionSimConfig",
    "Mapping",
    "_MarketRuleConfig",
    "_coerce_optional_str",
    "_coerce_positive_float",
    "_coerce_positive_int",
    "_resolve_liquidity_cols",
    "_resolve_market_rule_config",
    "_resolve_sell_max_days",
    "annotations",
    "build_execution_sim_config",
    "cast",
    "dataclass",
    "describe_execution_sim_config",
    "required_execution_sim_columns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.config import (
        SELL_UNTIL_NEXT_REBALANCE,
        Any,
        ExecutionSimConfig,
        Mapping,
        _coerce_optional_str,
        _coerce_positive_float,
        _coerce_positive_int,
        _MarketRuleConfig,
        _resolve_liquidity_cols,
        _resolve_market_rule_config,
        _resolve_sell_max_days,
        annotations,
        build_execution_sim_config,
        cast,
        dataclass,
        describe_execution_sim_config,
        required_execution_sim_columns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.config")
