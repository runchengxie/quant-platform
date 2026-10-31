"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "_cap_and_redistribute_allow_cash",
    "_eligible_round_lot_account_frame",
    "_finish_round_lot_account_diagnostics",
    "_floor_round_lot_account_allocations",
    "_redistribute_round_lot_account_cash",
    "_round_lot_account_candidates",
    "_round_lot_account_diagnostics",
    "_series_float",
    "allocate_round_lot",
    "allocate_round_lot_account",
    "annotations",
    "portfolio_value",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._round_lot_allocate import (
        Any,
        _cap_and_redistribute_allow_cash,
        _eligible_round_lot_account_frame,
        _finish_round_lot_account_diagnostics,
        _floor_round_lot_account_allocations,
        _redistribute_round_lot_account_cash,
        _round_lot_account_candidates,
        _round_lot_account_diagnostics,
        _series_float,
        allocate_round_lot,
        allocate_round_lot_account,
        annotations,
        portfolio_value,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._round_lot_allocate")
