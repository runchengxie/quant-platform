"""Compatibility alias for the Engine-owned quant_backtest_core.planning.multiperiod."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.planning.multiperiod import Bounds as Bounds
    from quant_backtest_core.planning.multiperiod import MultiPeriodPlan as MultiPeriodPlan
    from quant_backtest_core.planning.multiperiod import MultiPeriodRequest as MultiPeriodRequest
    from quant_backtest_core.planning.multiperiod import _inputs as _inputs
    from quant_backtest_core.planning.multiperiod import _parameters as _parameters
    from quant_backtest_core.planning.multiperiod import dataclass as dataclass
    from quant_backtest_core.planning.multiperiod import minimize as minimize
    from quant_backtest_core.planning.multiperiod import np as np
    from quant_backtest_core.planning.multiperiod import plan_trades as plan_trades

sys.modules[__name__] = import_module("quant_backtest_core.planning.multiperiod")
