"""Compatibility alias for the Engine-owned quant_backtest_core.microstructure.pack."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.microstructure.pack import Any as Any
    from quant_backtest_core.microstructure.pack import Iterable as Iterable
    from quant_backtest_core.microstructure.pack import Literal as Literal
    from quant_backtest_core.microstructure.pack import SimulatorEvent as SimulatorEvent
    from quant_backtest_core.microstructure.pack import SimulatorPack as SimulatorPack
    from quant_backtest_core.microstructure.pack import _optional_sequence as _optional_sequence
    from quant_backtest_core.microstructure.pack import build_simulator_pack as build_simulator_pack
    from quant_backtest_core.microstructure.pack import dataclass as dataclass
    from quant_backtest_core.microstructure.pack import field as field
    from quant_backtest_core.microstructure.pack import ordering_provenance as ordering_provenance
    from quant_backtest_core.microstructure.pack import (
        sort_simulator_events as sort_simulator_events,
    )

sys.modules[__name__] = import_module("quant_backtest_core.microstructure.pack")
