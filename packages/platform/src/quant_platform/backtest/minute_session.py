"""Compatibility module for the Engine-owned quant_backtest_core.backtest.minute_session."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.minute_session import _FIELDS as _FIELDS
    from quant_backtest_core.backtest.minute_session import Any as Any
    from quant_backtest_core.backtest.minute_session import CapitalFlow as CapitalFlow
    from quant_backtest_core.backtest.minute_session import CorporateAction as CorporateAction
    from quant_backtest_core.backtest.minute_session import LinearImpact as LinearImpact
    from quant_backtest_core.backtest.minute_session import MappingProxyType as MappingProxyType
    from quant_backtest_core.backtest.minute_session import MinuteSession as MinuteSession
    from quant_backtest_core.backtest.minute_session import QuantityLock as QuantityLock
    from quant_backtest_core.backtest.minute_session import ValuationEvent as ValuationEvent
    from quant_backtest_core.backtest.minute_session import _binding as _binding
    from quant_backtest_core.backtest.minute_session import _digest as _digest
    from quant_backtest_core.backtest.minute_session import _MinuteSimulation as _MinuteSimulation
    from quant_backtest_core.backtest.minute_session import _unwire as _unwire
    from quant_backtest_core.backtest.minute_session import _wire as _wire
    from quant_backtest_core.backtest.minute_session import annotations as annotations
    from quant_backtest_core.backtest.minute_session import asdict as asdict
    from quant_backtest_core.backtest.minute_session import initialize_capital as initialize_capital
    from quant_backtest_core.backtest.minute_session import json as json
    from quant_backtest_core.backtest.minute_session import math as math
    from quant_backtest_core.backtest.minute_session import pd as pd
    from quant_backtest_core.backtest.minute_session import replace as replace

sys.modules[__name__] = import_module("quant_backtest_core.backtest.minute_session")
