"""Compatibility module for the Engine-owned quant_backtest_core._minute.capital_flows."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core._minute.capital_flows import (
        CAPITAL_FLOW_COLUMNS as CAPITAL_FLOW_COLUMNS,
    )
    from quant_backtest_core._minute.capital_flows import CapitalFlow as CapitalFlow
    from quant_backtest_core._minute.capital_flows import ValuationEvent as ValuationEvent
    from quant_backtest_core._minute.capital_flows import apply_capital_flows as apply_capital_flows
    from quant_backtest_core._minute.capital_flows import capital_daily as capital_daily
    from quant_backtest_core._minute.capital_flows import dataclass as dataclass
    from quant_backtest_core._minute.capital_flows import datetime as datetime
    from quant_backtest_core._minute.capital_flows import initialize_capital as initialize_capital
    from quant_backtest_core._minute.capital_flows import isfinite as isfinite
    from quant_backtest_core._minute.capital_flows import marked_wealth as marked_wealth
    from quant_backtest_core._minute.capital_flows import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core._minute.capital_flows")
