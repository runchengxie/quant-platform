"""Compatibility alias for the Engine-owned quant_backtest_core.backtest.reconciliation."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.reconciliation import AccountEvidence as AccountEvidence
    from quant_backtest_core.backtest.reconciliation import Mapping as Mapping
    from quant_backtest_core.backtest.reconciliation import MappingProxyType as MappingProxyType
    from quant_backtest_core.backtest.reconciliation import OrderEvidence as OrderEvidence
    from quant_backtest_core.backtest.reconciliation import _name as _name
    from quant_backtest_core.backtest.reconciliation import _number as _number
    from quant_backtest_core.backtest.reconciliation import _shares as _shares
    from quant_backtest_core.backtest.reconciliation import dataclass as dataclass
    from quant_backtest_core.backtest.reconciliation import isfinite as isfinite
    from quant_backtest_core.backtest.reconciliation import reconcile_evidence as reconcile_evidence

sys.modules[__name__] = import_module("quant_backtest_core.backtest.reconciliation")
