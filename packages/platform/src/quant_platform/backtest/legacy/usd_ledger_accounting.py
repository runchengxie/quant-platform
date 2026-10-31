"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "QUANTITY_STEP",
    "ROUND_DOWN",
    "TRANSACTION_COLUMNS",
    "ZERO",
    "Decimal",
    "Mapping",
    "USDInstrument",
    "USDReplayConfig",
    "_apply_transaction",
    "_rates",
    "_round_increment",
    "_validate_settlement",
    "decimal_value",
    "localcontext",
    "require",
    "settle_usd_rebalance",
    "validate_usd_config",
    "value_usd_book",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.usd_ledger_accounting import (
        QUANTITY_STEP,
        ROUND_DOWN,
        TRANSACTION_COLUMNS,
        ZERO,
        Decimal,
        Mapping,
        USDInstrument,
        USDReplayConfig,
        _apply_transaction,
        _rates,
        _round_increment,
        _validate_settlement,
        decimal_value,
        localcontext,
        require,
        settle_usd_rebalance,
        validate_usd_config,
        value_usd_book,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.usd_ledger_accounting")
