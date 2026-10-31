"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "RoundLotVariant",
    "_numeric_series",
    "annotations",
    "cap_and_redistribute",
    "cast",
    "select_round_lot_targets",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._round_lot_targets import (
        Any,
        RoundLotVariant,
        _numeric_series,
        annotations,
        cap_and_redistribute,
        cast,
        select_round_lot_targets,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._round_lot_targets")
