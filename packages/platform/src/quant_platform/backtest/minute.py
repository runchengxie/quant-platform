"""Compatibility module for the Engine-owned quant_backtest_core.backtest.minute."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.minute import CapitalFlow as CapitalFlow
    from quant_backtest_core.backtest.minute import CorporateAction as CorporateAction
    from quant_backtest_core.backtest.minute import MinuteDecisionState as MinuteDecisionState
    from quant_backtest_core.backtest.minute import MinuteExecutionConfig as MinuteExecutionConfig
    from quant_backtest_core.backtest.minute import MinuteExecutionResult as MinuteExecutionResult
    from quant_backtest_core.backtest.minute import ValuationEvent as ValuationEvent
    from quant_backtest_core.backtest.minute import (
        simulate_minute_execution as simulate_minute_execution,
    )

sys.modules[__name__] = import_module("quant_backtest_core.backtest.minute")
