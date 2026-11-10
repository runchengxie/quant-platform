"""Compatibility alias for the Engine-owned quant_backtest_core.backtest.ledger."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.ledger import UnifiedLedger as UnifiedLedger
    from quant_backtest_core.backtest.ledger import _require_columns as _require_columns
    from quant_backtest_core.backtest.ledger import dataclass as dataclass
    from quant_backtest_core.backtest.ledger import pd as pd
    from quant_backtest_core.backtest.ledger import (
        reconcile_unified_ledger as reconcile_unified_ledger,
    )
    from quant_backtest_core.backtest.ledger import validate_ledger_frames as validate_ledger_frames

sys.modules[__name__] = import_module("quant_backtest_core.backtest.ledger")
