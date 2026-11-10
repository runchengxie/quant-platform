"""Compatibility alias for the Engine-owned quant_backtest_core.daily._execution_models."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily._execution_models import MARKET_CALENDAR as MARKET_CALENDAR
    from quant_backtest_core.daily._execution_models import BpsCostModel as BpsCostModel
    from quant_backtest_core.daily._execution_models import BpsSlippageModel as BpsSlippageModel
    from quant_backtest_core.daily._execution_models import CostModel as CostModel
    from quant_backtest_core.daily._execution_models import (
        DetailedTradeFeeModel as DetailedTradeFeeModel,
    )
    from quant_backtest_core.daily._execution_models import EntryPolicy as EntryPolicy
    from quant_backtest_core.daily._execution_models import ExecutionModel as ExecutionModel
    from quant_backtest_core.daily._execution_models import ExitFallbackPolicy as ExitFallbackPolicy
    from quant_backtest_core.daily._execution_models import ExitPolicy as ExitPolicy
    from quant_backtest_core.daily._execution_models import ExitPricePolicy as ExitPricePolicy
    from quant_backtest_core.daily._execution_models import Literal as Literal
    from quant_backtest_core.daily._execution_models import NoCostModel as NoCostModel
    from quant_backtest_core.daily._execution_models import NoSlippageModel as NoSlippageModel
    from quant_backtest_core.daily._execution_models import (
        ParticipationSlippageModel as ParticipationSlippageModel,
    )
    from quant_backtest_core.daily._execution_models import Protocol as Protocol
    from quant_backtest_core.daily._execution_models import (
        SelectionConstraints as SelectionConstraints,
    )
    from quant_backtest_core.daily._execution_models import SideBpsCostModel as SideBpsCostModel
    from quant_backtest_core.daily._execution_models import SlippageModel as SlippageModel
    from quant_backtest_core.daily._execution_models import dataclass as dataclass
    from quant_backtest_core.daily._execution_models import np as np
    from quant_backtest_core.daily._execution_models import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily._execution_models")
