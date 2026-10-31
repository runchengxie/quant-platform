"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "EconomicRebalanceResult",
    "Mapping",
    "_validate_weights",
    "annotations",
    "apply_no_trade_band",
    "dataclass",
    "field",
    "isfinite",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.economic_rebalance import (
        Any,
        EconomicRebalanceResult,
        Mapping,
        _validate_weights,
        annotations,
        apply_no_trade_band,
        dataclass,
        field,
        isfinite,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.economic_rebalance")
