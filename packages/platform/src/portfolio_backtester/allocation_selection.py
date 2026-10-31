"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Path",
    "_ensure_symbol_column",
    "annotations",
    "cast",
    "prepare_selection",
    "select_from_positions_file",
    "select_latest_holdings",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.allocation_selection import (
        Path,
        _ensure_symbol_column,
        annotations,
        cast,
        prepare_selection,
        select_from_positions_file,
        select_latest_holdings,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.allocation_selection")
