"""Compatibility alias for the Engine-owned quant_backtest_core.backtest.paper_account."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.paper_account import HouseMargin as HouseMargin
    from quant_backtest_core.backtest.paper_account import Literal as Literal
    from quant_backtest_core.backtest.paper_account import Mapping as Mapping
    from quant_backtest_core.backtest.paper_account import MappingProxyType as MappingProxyType
    from quant_backtest_core.backtest.paper_account import Observed as Observed
    from quant_backtest_core.backtest.paper_account import PaperFill as PaperFill
    from quant_backtest_core.backtest.paper_account import PaperProjection as PaperProjection
    from quant_backtest_core.backtest.paper_account import PaperState as PaperState
    from quant_backtest_core.backtest.paper_account import Sequence as Sequence
    from quant_backtest_core.backtest.paper_account import _accrue_opening as _accrue_opening
    from quant_backtest_core.backtest.paper_account import _apply_fills as _apply_fills
    from quant_backtest_core.backtest.paper_account import _funding_principal as _funding_principal
    from quant_backtest_core.backtest.paper_account import _interval as _interval
    from quant_backtest_core.backtest.paper_account import _inventory as _inventory
    from quant_backtest_core.backtest.paper_account import _number as _number
    from quant_backtest_core.backtest.paper_account import _observed as _observed
    from quant_backtest_core.backtest.paper_account import _symbol as _symbol
    from quant_backtest_core.backtest.paper_account import _timestamp as _timestamp
    from quant_backtest_core.backtest.paper_account import dataclass as dataclass
    from quant_backtest_core.backtest.paper_account import field as field
    from quant_backtest_core.backtest.paper_account import isfinite as isfinite
    from quant_backtest_core.backtest.paper_account import pd as pd
    from quant_backtest_core.backtest.paper_account import (
        project_paper_account as project_paper_account,
    )

sys.modules[__name__] = import_module("quant_backtest_core.backtest.paper_account")
