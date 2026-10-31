"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Literal",
    "RoundLotVariant",
    "WeightingMode",
    "_cap_and_redistribute_allow_cash",
    "_numeric_series",
    "_series_float",
    "annotations",
    "cap_and_redistribute",
    "dataclass",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._round_lot_weights import (
        Any,
        Literal,
        RoundLotVariant,
        WeightingMode,
        _cap_and_redistribute_allow_cash,
        _numeric_series,
        _series_float,
        annotations,
        cap_and_redistribute,
        dataclass,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._round_lot_weights")
