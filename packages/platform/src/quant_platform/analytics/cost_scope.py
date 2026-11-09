"""Compatibility module for the Engine-owned quant_backtest_core.evidence.cost_scope."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.evidence.cost_scope import ScopedCostModel as ScopedCostModel
    from quant_backtest_core.evidence.cost_scope import _frame as _frame
    from quant_backtest_core.evidence.cost_scope import _numeric as _numeric
    from quant_backtest_core.evidence.cost_scope import _supported_cost_rows as _supported_cost_rows
    from quant_backtest_core.evidence.cost_scope import annotations as annotations
    from quant_backtest_core.evidence.cost_scope import dataclass as dataclass
    from quant_backtest_core.evidence.cost_scope import fit_cost_scope as fit_cost_scope
    from quant_backtest_core.evidence.cost_scope import nnls as nnls
    from quant_backtest_core.evidence.cost_scope import np as np
    from quant_backtest_core.evidence.cost_scope import pd as pd
    from quant_backtest_core.evidence.cost_scope import validate_cost_scope as validate_cost_scope
    from quant_backtest_core.evidence.cost_scope import (
        validate_cost_scope_uncertainty as validate_cost_scope_uncertainty,
    )

sys.modules[__name__] = import_module("quant_backtest_core.evidence.cost_scope")
