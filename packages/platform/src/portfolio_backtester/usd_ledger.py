"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DAILY_COLUMNS",
    "HOLDING_COLUMNS",
    "MARK_METADATA_COLUMNS",
    "TARGET_COLUMNS",
    "TRANSACTION_COLUMNS",
    "ZERO",
    "Any",
    "Decimal",
    "USDRebalanceDecision",
    "USDReplayRequest",
    "USDReplayResult",
    "_Replay",
    "_mark_metadata",
    "_summary",
    "assert_usd_equal",
    "datetime",
    "defaultdict",
    "localcontext",
    "require",
    "run_usd_price_replay",
    "select_usd_fx",
    "select_usd_modeled_execution_price",
    "select_usd_price",
    "settle_usd_rebalance",
    "validate_usd_request",
    "value_usd_book",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.usd_ledger import (
        DAILY_COLUMNS,
        HOLDING_COLUMNS,
        MARK_METADATA_COLUMNS,
        TARGET_COLUMNS,
        TRANSACTION_COLUMNS,
        ZERO,
        Any,
        Decimal,
        USDRebalanceDecision,
        USDReplayRequest,
        USDReplayResult,
        _mark_metadata,
        _Replay,
        _summary,
        assert_usd_equal,
        datetime,
        defaultdict,
        localcontext,
        require,
        run_usd_price_replay,
        select_usd_fx,
        select_usd_modeled_execution_price,
        select_usd_price,
        settle_usd_rebalance,
        validate_usd_request,
        value_usd_book,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.usd_ledger")
