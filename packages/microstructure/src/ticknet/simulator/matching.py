"""Compatibility alias for the Engine-owned quant_backtest_core.microstructure.matching."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.microstructure.matching import Fill as Fill
    from quant_backtest_core.microstructure.matching import LimitOrderBook as LimitOrderBook
    from quant_backtest_core.microstructure.matching import Literal as Literal
    from quant_backtest_core.microstructure.matching import MatchingEngine as MatchingEngine
    from quant_backtest_core.microstructure.matching import Protocol as Protocol
    from quant_backtest_core.microstructure.matching import RestingOrder as RestingOrder
    from quant_backtest_core.microstructure.matching import SimulatorEvent as SimulatorEvent
    from quant_backtest_core.microstructure.matching import Trade as Trade
    from quant_backtest_core.microstructure.matching import _RustOrderBook as _RustOrderBook
    from quant_backtest_core.microstructure.matching import cast as cast
    from quant_backtest_core.microstructure.matching import dataclass as dataclass

sys.modules[__name__] = import_module("quant_backtest_core.microstructure.matching")
