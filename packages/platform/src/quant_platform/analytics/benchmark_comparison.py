"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "_input_hash",
    "_validated_returns",
    "_validated_weights",
    "annotations",
    "build_comparison_receipt",
    "compare_portfolio_returns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.benchmark_comparison import (
        Any,
        Mapping,
        _input_hash,
        _validated_returns,
        _validated_weights,
        annotations,
        build_comparison_receipt,
        compare_portfolio_returns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.benchmark_comparison")
