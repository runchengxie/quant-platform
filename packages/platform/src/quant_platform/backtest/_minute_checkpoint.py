"""Compatibility module for the Engine-owned quant_backtest_core.backtest._minute_checkpoint."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest._minute_checkpoint import _EVENT_TYPES as _EVENT_TYPES
    from quant_backtest_core.backtest._minute_checkpoint import _FIELDS as _FIELDS
    from quant_backtest_core.backtest._minute_checkpoint import CapitalFlow as CapitalFlow
    from quant_backtest_core.backtest._minute_checkpoint import CorporateAction as CorporateAction
    from quant_backtest_core.backtest._minute_checkpoint import LinearImpact as LinearImpact
    from quant_backtest_core.backtest._minute_checkpoint import Path as Path
    from quant_backtest_core.backtest._minute_checkpoint import QuantityLock as QuantityLock
    from quant_backtest_core.backtest._minute_checkpoint import ValuationEvent as ValuationEvent
    from quant_backtest_core.backtest._minute_checkpoint import _binding as _binding
    from quant_backtest_core.backtest._minute_checkpoint import _digest as _digest
    from quant_backtest_core.backtest._minute_checkpoint import _frame_binding as _frame_binding
    from quant_backtest_core.backtest._minute_checkpoint import (
        _MinuteSimulation as _MinuteSimulation,
    )
    from quant_backtest_core.backtest._minute_checkpoint import _nonfinite as _nonfinite
    from quant_backtest_core.backtest._minute_checkpoint import _unwire as _unwire
    from quant_backtest_core.backtest._minute_checkpoint import _wire as _wire
    from quant_backtest_core.backtest._minute_checkpoint import asdict as asdict
    from quant_backtest_core.backtest._minute_checkpoint import date as date
    from quant_backtest_core.backtest._minute_checkpoint import hashlib as hashlib
    from quant_backtest_core.backtest._minute_checkpoint import inspect as inspect
    from quant_backtest_core.backtest._minute_checkpoint import json as json
    from quant_backtest_core.backtest._minute_checkpoint import math as math
    from quant_backtest_core.backtest._minute_checkpoint import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.backtest._minute_checkpoint")
