"""Compatibility module for the Engine-owned quant_backtest_core.backtest.quantity_locks."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.quantity_locks import QuantityLock as QuantityLock
    from quant_backtest_core.backtest.quantity_locks import dataclass as dataclass

sys.modules[__name__] = import_module("quant_backtest_core.backtest.quantity_locks")
