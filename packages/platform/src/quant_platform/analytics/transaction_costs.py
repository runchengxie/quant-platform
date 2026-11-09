"""Compatibility module for the Engine-owned quant_backtest_core.evidence.transaction_costs."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.evidence.transaction_costs import _FILL_COLUMNS as _FILL_COLUMNS
    from quant_backtest_core.evidence.transaction_costs import (
        _OBSERVATION_COLUMNS as _OBSERVATION_COLUMNS,
    )
    from quant_backtest_core.evidence.transaction_costs import _PARENT_COLUMNS as _PARENT_COLUMNS
    from quant_backtest_core.evidence.transaction_costs import ROUND_HALF_UP as ROUND_HALF_UP
    from quant_backtest_core.evidence.transaction_costs import (
        CostEvidenceReport as CostEvidenceReport,
    )
    from quant_backtest_core.evidence.transaction_costs import Decimal as Decimal
    from quant_backtest_core.evidence.transaction_costs import Integral as Integral
    from quant_backtest_core.evidence.transaction_costs import _canonical as _canonical
    from quant_backtest_core.evidence.transaction_costs import _cents as _cents
    from quant_backtest_core.evidence.transaction_costs import _clock as _clock
    from quant_backtest_core.evidence.transaction_costs import _components as _components
    from quant_backtest_core.evidence.transaction_costs import _deduplicate as _deduplicate
    from quant_backtest_core.evidence.transaction_costs import _digest as _digest
    from quant_backtest_core.evidence.transaction_costs import _fees as _fees
    from quant_backtest_core.evidence.transaction_costs import _fill as _fill
    from quant_backtest_core.evidence.transaction_costs import _identity as _identity
    from quant_backtest_core.evidence.transaction_costs import _liquidity as _liquidity
    from quant_backtest_core.evidence.transaction_costs import _missing as _missing
    from quant_backtest_core.evidence.transaction_costs import _number as _number
    from quant_backtest_core.evidence.transaction_costs import _optional_quote as _optional_quote
    from quant_backtest_core.evidence.transaction_costs import _parent as _parent
    from quant_backtest_core.evidence.transaction_costs import _recorded_fees as _recorded_fees
    from quant_backtest_core.evidence.transaction_costs import _text as _text
    from quant_backtest_core.evidence.transaction_costs import annotations as annotations
    from quant_backtest_core.evidence.transaction_costs import (
        audit_transaction_costs as audit_transaction_costs,
    )
    from quant_backtest_core.evidence.transaction_costs import dataclass as dataclass
    from quant_backtest_core.evidence.transaction_costs import hashlib as hashlib
    from quant_backtest_core.evidence.transaction_costs import json as json
    from quant_backtest_core.evidence.transaction_costs import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.evidence.transaction_costs")
