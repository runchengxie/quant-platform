"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "_group_shares",
    "_hhi",
    "_liquidity_bucket",
    "annotations",
    "concentration_by_group",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._capacity_concentration import (
        Any,
        _group_shares,
        _hhi,
        _liquidity_bucket,
        annotations,
        concentration_by_group,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._capacity_concentration")
