"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Literal",
    "Path",
    "SizingConfig",
    "_cap_and_redistribute",
    "_constrain_sized_weights",
    "_normal_cdf",
    "_normalize_gross",
    "_raw_sizing_values",
    "_scale_by_volatility",
    "annotations",
    "asdict",
    "average_active_bets",
    "build_sized_weights",
    "build_sizing_receipt",
    "dataclass",
    "discretize_weights",
    "erf",
    "probability_to_size",
    "sqrt",
    "write_sizing_receipt",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.bet_sizing import (
        Literal,
        Path,
        SizingConfig,
        _cap_and_redistribute,
        _constrain_sized_weights,
        _normal_cdf,
        _normalize_gross,
        _raw_sizing_values,
        _scale_by_volatility,
        annotations,
        asdict,
        average_active_bets,
        build_sized_weights,
        build_sizing_receipt,
        dataclass,
        discretize_weights,
        erf,
        probability_to_size,
        sqrt,
        write_sizing_receipt,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.bet_sizing")
