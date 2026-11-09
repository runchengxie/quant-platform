"""Compatibility module for the Engine-owned quant_backtest_core.backtest.impact."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.impact import LinearImpact as LinearImpact
    from quant_backtest_core.backtest.impact import _State as _State
    from quant_backtest_core.backtest.impact import annotations as annotations
    from quant_backtest_core.backtest.impact import asdict as asdict
    from quant_backtest_core.backtest.impact import dataclass as dataclass
    from quant_backtest_core.backtest.impact import math as math

sys.modules[__name__] = import_module("quant_backtest_core.backtest.impact")
