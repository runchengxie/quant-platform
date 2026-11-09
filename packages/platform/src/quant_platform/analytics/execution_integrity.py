"""Compatibility module for the Engine-owned quant_backtest_core.evidence.execution_integrity."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.evidence.execution_integrity import Decimal as Decimal
    from quant_backtest_core.evidence.execution_integrity import _clock as _clock
    from quant_backtest_core.evidence.execution_integrity import _decimal as _decimal
    from quant_backtest_core.evidence.execution_integrity import _exact as _exact
    from quant_backtest_core.evidence.execution_integrity import _quantities as _quantities
    from quant_backtest_core.evidence.execution_integrity import _shares as _shares
    from quant_backtest_core.evidence.execution_integrity import (
        compare_prefixes as compare_prefixes,
    )
    from quant_backtest_core.evidence.execution_integrity import defaultdict as defaultdict
    from quant_backtest_core.evidence.execution_integrity import exit_wealth as exit_wealth
    from quant_backtest_core.evidence.execution_integrity import fill_prefixes as fill_prefixes
    from quant_backtest_core.evidence.execution_integrity import pairwise as pairwise

sys.modules[__name__] = import_module("quant_backtest_core.evidence.execution_integrity")
