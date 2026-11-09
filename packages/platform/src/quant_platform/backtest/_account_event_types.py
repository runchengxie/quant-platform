"""Compatibility alias for the Engine-owned quant_backtest_core.backtest._account_event_types."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest._account_event_types import Any as Any
    from quant_backtest_core.backtest._account_event_types import TypedDict as TypedDict
    from quant_backtest_core.backtest._account_event_types import _AccountData as _AccountData
    from quant_backtest_core.backtest._account_event_types import _Entitlement as _Entitlement
    from quant_backtest_core.backtest._account_event_types import _Order as _Order
    from quant_backtest_core.backtest._account_event_types import _Reduction as _Reduction
    from quant_backtest_core.backtest._account_event_types import _Report as _Report
    from quant_backtest_core.backtest._account_event_types import _Settlement as _Settlement
    from quant_backtest_core.backtest._account_event_types import _StateWire as _StateWire

sys.modules[__name__] = import_module("quant_backtest_core.backtest._account_event_types")
