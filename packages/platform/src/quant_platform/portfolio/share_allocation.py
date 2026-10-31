"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["ShareAllocationResult", "allocate_equal_weight_shares", "annotations", "dataclass"]

if TYPE_CHECKING:
    from quant_platform._portfolio.share_allocation import (
        ShareAllocationResult,
        allocate_equal_weight_shares,
        annotations,
        dataclass,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.share_allocation")
