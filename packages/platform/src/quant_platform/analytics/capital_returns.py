"""Compatibility module for the Engine-owned quant_backtest_core.evidence.capital_returns."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.evidence.capital_returns import (
        CapitalObservation as CapitalObservation,
    )
    from quant_backtest_core.evidence.capital_returns import _number as _number
    from quant_backtest_core.evidence.capital_returns import (
        capital_performance as capital_performance,
    )
    from quant_backtest_core.evidence.capital_returns import dataclass as dataclass
    from quant_backtest_core.evidence.capital_returns import fsum as fsum
    from quant_backtest_core.evidence.capital_returns import isclose as isclose
    from quant_backtest_core.evidence.capital_returns import isfinite as isfinite
    from quant_backtest_core.evidence.capital_returns import prod as prod
    from quant_backtest_core.evidence.capital_returns import ulp as ulp

sys.modules[__name__] = import_module("quant_backtest_core.evidence.capital_returns")
