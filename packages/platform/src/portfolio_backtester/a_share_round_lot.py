"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "RoundLotVariant",
    "allocate_round_lot",
    "allocate_round_lot_account",
    "annotations",
    "cap_and_redistribute",
    "portfolio_value",
    "select_round_lot_targets",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.a_share_round_lot import (
        RoundLotVariant,
        allocate_round_lot,
        allocate_round_lot_account,
        annotations,
        cap_and_redistribute,
        portfolio_value,
        select_round_lot_targets,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.a_share_round_lot")
