"""Compatibility alias for the Engine-owned quant_backtest_core.microstructure.replay."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.microstructure.replay import BackgroundOrder as BackgroundOrder
    from quant_backtest_core.microstructure.replay import Fill as Fill
    from quant_backtest_core.microstructure.replay import Integral as Integral
    from quant_backtest_core.microstructure.replay import InterventionOrder as InterventionOrder
    from quant_backtest_core.microstructure.replay import MatchingEngine as MatchingEngine
    from quant_backtest_core.microstructure.replay import ReplayFill as ReplayFill
    from quant_backtest_core.microstructure.replay import ReplaySession as ReplaySession
    from quant_backtest_core.microstructure.replay import Tick as Tick
    from quant_backtest_core.microstructure.replay import Trade as Trade
    from quant_backtest_core.microstructure.replay import _integer_time_ms as _integer_time_ms
    from quant_backtest_core.microstructure.replay import dataclass as dataclass

sys.modules[__name__] = import_module("quant_backtest_core.microstructure.replay")
