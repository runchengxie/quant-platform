"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "AllocationReference",
    "EqualWeightAllocation",
    "Path",
    "allocate_equal_weight_shares",
    "annotations",
    "build_equal_weight_allocation",
    "dataclass",
    "join_allocation_reference",
    "load_allocation_reference",
    "prepare_selection",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.allocation_service import (
        AllocationReference,
        EqualWeightAllocation,
        Path,
        allocate_equal_weight_shares,
        annotations,
        build_equal_weight_allocation,
        dataclass,
        join_allocation_reference,
        load_allocation_reference,
        prepare_selection,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.allocation_service")
