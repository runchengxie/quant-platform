"""Compatibility module for the Engine-owned quant_backtest_core.backtest.costs."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.costs import COST_EVIDENCE_SCHEMA as COST_EVIDENCE_SCHEMA
    from quant_backtest_core.backtest.costs import Any as Any
    from quant_backtest_core.backtest.costs import CostComponents as CostComponents
    from quant_backtest_core.backtest.costs import CostEvidence as CostEvidence
    from quant_backtest_core.backtest.costs import CostGroup as CostGroup
    from quant_backtest_core.backtest.costs import Mapping as Mapping
    from quant_backtest_core.backtest.costs import MappingProxyType as MappingProxyType
    from quant_backtest_core.backtest.costs import _finite as _finite
    from quant_backtest_core.backtest.costs import annotations as annotations
    from quant_backtest_core.backtest.costs import asdict as asdict
    from quant_backtest_core.backtest.costs import dataclass as dataclass
    from quant_backtest_core.backtest.costs import field as field
    from quant_backtest_core.backtest.costs import isclose as isclose
    from quant_backtest_core.backtest.costs import isfinite as isfinite

sys.modules[__name__] = import_module("quant_backtest_core.backtest.costs")
