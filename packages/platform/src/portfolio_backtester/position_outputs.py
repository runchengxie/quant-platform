"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Path",
    "_build_rebalance_diff",
    "_coerce_yyyymmdd",
    "_save_frame",
    "annotations",
    "canonicalize_symbol_columns",
    "write_position_outputs",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.position_outputs import (
        Any,
        Path,
        _build_rebalance_diff,
        _coerce_yyyymmdd,
        _save_frame,
        annotations,
        canonicalize_symbol_columns,
        write_position_outputs,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.position_outputs")
