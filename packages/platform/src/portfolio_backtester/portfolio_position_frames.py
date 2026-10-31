"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "annotations",
    "canonicalize_symbol_columns",
    "normalize_portfolio_frames",
    "resolve_pricing_source",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.portfolio_position_frames import (
        annotations,
        canonicalize_symbol_columns,
        normalize_portfolio_frames,
        resolve_pricing_source,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.portfolio_position_frames")
