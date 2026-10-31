"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Literal",
    "NaTType",
    "PositionBacktestConfig",
    "PositionBacktestResult",
    "PositionExitPolicy",
    "_date_key",
    "_date_series",
    "_date_value",
    "annotations",
    "assert_positions_by_rebalance_frame",
    "cast",
    "dataclass",
    "normalize_position_backtest_periods",
    "normalize_position_backtest_positions",
    "normalize_position_backtest_pricing",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._position_backtest_config import (
        Any,
        Literal,
        NaTType,
        PositionBacktestConfig,
        PositionBacktestResult,
        PositionExitPolicy,
        _date_key,
        _date_series,
        _date_value,
        annotations,
        assert_positions_by_rebalance_frame,
        cast,
        dataclass,
        normalize_position_backtest_periods,
        normalize_position_backtest_positions,
        normalize_position_backtest_pricing,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._position_backtest_config")
