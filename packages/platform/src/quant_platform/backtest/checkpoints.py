"""Compatibility alias for the Engine-owned quant_backtest_core.backtest.checkpoints."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.checkpoints import AccountEventAdapter as AccountEventAdapter
    from quant_backtest_core.backtest.checkpoints import ExecutionState as ExecutionState
    from quant_backtest_core.backtest.checkpoints import LinearImpact as LinearImpact
    from quant_backtest_core.backtest.checkpoints import _digest as _digest
    from quant_backtest_core.backtest.checkpoints import _encoded as _encoded
    from quant_backtest_core.backtest.checkpoints import deepcopy as deepcopy
    from quant_backtest_core.backtest.checkpoints import hashlib as hashlib
    from quant_backtest_core.backtest.checkpoints import json as json
    from quant_backtest_core.backtest.checkpoints import replace as replace

sys.modules[__name__] = import_module("quant_backtest_core.backtest.checkpoints")
