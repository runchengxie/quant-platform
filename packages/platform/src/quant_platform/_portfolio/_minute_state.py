"""Compatibility module for the Engine-owned quant_backtest_core._minute._minute_state."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core._minute._minute_state import Mapping as Mapping
    from quant_backtest_core._minute._minute_state import MinuteDecisionState as MinuteDecisionState
    from quant_backtest_core._minute._minute_state import dataclass as dataclass
    from quant_backtest_core._minute._minute_state import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core._minute._minute_state")
