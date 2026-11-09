"""Compatibility module for the Engine-owned quant_backtest_core._minute.valuation_events."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core._minute.valuation_events import (
        VALUATION_LEDGER_COLUMNS as VALUATION_LEDGER_COLUMNS,
    )
    from quant_backtest_core._minute.valuation_events import Iterable as Iterable
    from quant_backtest_core._minute.valuation_events import ValuationEvent as ValuationEvent
    from quant_backtest_core._minute.valuation_events import _market_timezone as _market_timezone
    from quant_backtest_core._minute.valuation_events import annotations as annotations
    from quant_backtest_core._minute.valuation_events import cast as cast
    from quant_backtest_core._minute.valuation_events import dataclass as dataclass
    from quant_backtest_core._minute.valuation_events import datetime as datetime
    from quant_backtest_core._minute.valuation_events import isfinite as isfinite
    from quant_backtest_core._minute.valuation_events import (
        minute_valuation_provenance as minute_valuation_provenance,
    )
    from quant_backtest_core._minute.valuation_events import (
        normalize_valuation_events as normalize_valuation_events,
    )
    from quant_backtest_core._minute.valuation_events import pd as pd
    from quant_backtest_core._minute.valuation_events import replace as replace

sys.modules[__name__] = import_module("quant_backtest_core._minute.valuation_events")
