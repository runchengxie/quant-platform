"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "annotations",
    "apply_rank_offset",
    "apply_rebalance_buffer",
    "canonicalize_symbol_columns",
    "estimate_turnover",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._metrics_turnover import (
        annotations,
        apply_rank_offset,
        apply_rebalance_buffer,
        canonicalize_symbol_columns,
        estimate_turnover,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._metrics_turnover")
