"""Compatibility alias for the Engine-owned quant_backtest_core.microstructure.impact."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.microstructure.impact import ExecutionSchedule as ExecutionSchedule
    from quant_backtest_core.microstructure.impact import ImpactEstimator as ImpactEstimator
    from quant_backtest_core.microstructure.impact import ImpactResult as ImpactResult
    from quant_backtest_core.microstructure.impact import InterventionOrder as InterventionOrder
    from quant_backtest_core.microstructure.impact import ReplayFill as ReplayFill
    from quant_backtest_core.microstructure.impact import ReplaySession as ReplaySession
    from quant_backtest_core.microstructure.impact import _mid as _mid
    from quant_backtest_core.microstructure.impact import dataclass as dataclass

sys.modules[__name__] = import_module("quant_backtest_core.microstructure.impact")
