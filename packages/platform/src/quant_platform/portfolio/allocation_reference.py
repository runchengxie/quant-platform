"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "REQUIRED_REFERENCE_COLUMNS",
    "AllocationReference",
    "Path",
    "_load_frame",
    "_normalize_order_book_ids",
    "_normalize_reference_dates",
    "_normalize_reference_prices",
    "_normalize_reference_symbols",
    "_reference_source",
    "_require_reference_columns",
    "annotations",
    "dataclass",
    "join_allocation_reference",
    "load_allocation_reference",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.allocation_reference import (
        REQUIRED_REFERENCE_COLUMNS,
        AllocationReference,
        Path,
        _load_frame,
        _normalize_order_book_ids,
        _normalize_reference_dates,
        _normalize_reference_prices,
        _normalize_reference_symbols,
        _reference_source,
        _require_reference_columns,
        annotations,
        dataclass,
        join_allocation_reference,
        load_allocation_reference,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.allocation_reference")
