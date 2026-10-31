"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "SupportsFloat",
    "annotations",
    "cast",
    "display_width",
    "format_allocation_csv",
    "format_allocation_text",
    "format_table",
    "safe_float",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.allocation_rendering import (
        SupportsFloat,
        annotations,
        cast,
        display_width,
        format_allocation_csv,
        format_allocation_text,
        format_table,
        safe_float,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.allocation_rendering")
