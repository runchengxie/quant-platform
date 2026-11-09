"""Compatibility alias for the Engine-owned quant_backtest_core.microstructure.correctness."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.microstructure.correctness import (
        CorrectnessResult as CorrectnessResult,
    )
    from quant_backtest_core.microstructure.correctness import Literal as Literal
    from quant_backtest_core.microstructure.correctness import MatchingEngine as MatchingEngine
    from quant_backtest_core.microstructure.correctness import SimulatorEvent as SimulatorEvent
    from quant_backtest_core.microstructure.correctness import SimulatorPack as SimulatorPack
    from quant_backtest_core.microstructure.correctness import _apply_event as _apply_event
    from quant_backtest_core.microstructure.correctness import dataclass as dataclass
    from quant_backtest_core.microstructure.correctness import (
        replay_and_compare as replay_and_compare,
    )

sys.modules[__name__] = import_module("quant_backtest_core.microstructure.correctness")
