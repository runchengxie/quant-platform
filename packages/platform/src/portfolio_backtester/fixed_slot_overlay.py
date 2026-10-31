"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_REQUIRED_COLUMNS",
    "FixedSlotOverlayError",
    "FixedSlotOverlayTarget",
    "_normalize_symbols",
    "_positive_int",
    "_validate_ranking",
    "annotations",
    "build_fixed_slot_overlay_target",
    "dataclass",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.fixed_slot_overlay import (
        _REQUIRED_COLUMNS,
        FixedSlotOverlayError,
        FixedSlotOverlayTarget,
        _normalize_symbols,
        _positive_int,
        _validate_ranking,
        annotations,
        build_fixed_slot_overlay_target,
        dataclass,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.fixed_slot_overlay")
