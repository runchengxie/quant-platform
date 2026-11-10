"""Compatibility alias for the Engine-owned quant_backtest_core.daily.dated_fees."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.dated_fees import Any as Any
    from quant_backtest_core.daily.dated_fees import DatedFeeQuote as DatedFeeQuote
    from quant_backtest_core.daily.dated_fees import DatedFeeSchedule as DatedFeeSchedule
    from quant_backtest_core.daily.dated_fees import DatedTradeFeeModel as DatedTradeFeeModel
    from quant_backtest_core.daily.dated_fees import FeeQuoteContext as FeeQuoteContext
    from quant_backtest_core.daily.dated_fees import FeeSchedulePeriod as FeeSchedulePeriod
    from quant_backtest_core.daily.dated_fees import Literal as Literal
    from quant_backtest_core.daily.dated_fees import Mapping as Mapping
    from quant_backtest_core.daily.dated_fees import MappingProxyType as MappingProxyType
    from quant_backtest_core.daily.dated_fees import Side as Side
    from quant_backtest_core.daily.dated_fees import _as_date as _as_date
    from quant_backtest_core.daily.dated_fees import _non_negative_finite as _non_negative_finite
    from quant_backtest_core.daily.dated_fees import dataclass as dataclass
    from quant_backtest_core.daily.dated_fees import date as date
    from quant_backtest_core.daily.dated_fees import datetime as datetime
    from quant_backtest_core.daily.dated_fees import math as math
    from quant_backtest_core.daily.dated_fees import pairwise as pairwise

sys.modules[__name__] = import_module("quant_backtest_core.daily.dated_fees")
