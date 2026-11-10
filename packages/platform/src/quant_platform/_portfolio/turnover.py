"""Compatibility alias for the Engine-owned quant_backtest_core.daily.turnover."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.turnover import Iterable as Iterable
    from quant_backtest_core.daily.turnover import (
        RebalanceTurnoverReport as RebalanceTurnoverReport,
    )
    from quant_backtest_core.daily.turnover import TurnoverBreakdown as TurnoverBreakdown
    from quant_backtest_core.daily.turnover import _aligned_weight_delta as _aligned_weight_delta
    from quant_backtest_core.daily.turnover import _normalized_name_set as _normalized_name_set
    from quant_backtest_core.daily.turnover import _target_name_changes as _target_name_changes
    from quant_backtest_core.daily.turnover import annualize_turnover as annualize_turnover
    from quant_backtest_core.daily.turnover import (
        build_rebalance_turnover_report as build_rebalance_turnover_report,
    )
    from quant_backtest_core.daily.turnover import dataclass as dataclass
    from quant_backtest_core.daily.turnover import name_turnover as name_turnover
    from quant_backtest_core.daily.turnover import np as np
    from quant_backtest_core.daily.turnover import pd as pd
    from quant_backtest_core.daily.turnover import (
        turnover_from_trade_weights as turnover_from_trade_weights,
    )

sys.modules[__name__] = import_module("quant_backtest_core.daily.turnover")
