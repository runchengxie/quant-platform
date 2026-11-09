"""Compatibility module for the Engine-owned quant_backtest_core.backtest.stress."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.stress import JointStress as JointStress
    from quant_backtest_core.backtest.stress import annotations as annotations
    from quant_backtest_core.backtest.stress import asdict as asdict
    from quant_backtest_core.backtest.stress import dataclass as dataclass
    from quant_backtest_core.backtest.stress import hashlib as hashlib
    from quant_backtest_core.backtest.stress import json as json
    from quant_backtest_core.backtest.stress import keyed_uniform as keyed_uniform
    from quant_backtest_core.backtest.stress import math as math
    from quant_backtest_core.backtest.stress import pd as pd
    from quant_backtest_core.backtest.stress import stress_bars as stress_bars

sys.modules[__name__] = import_module("quant_backtest_core.backtest.stress")
