"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_block_frame",
    "_daily_record",
    "_execution_schedule",
    "_exposure_schedule",
    "_has_directional_trade_block",
    "_has_suspension_conflict",
    "_log_holdings",
    "_map_targets_to_execution_dates",
    "_post_cost_nav",
    "_scheduled_target_state",
    "_validate_price_calendar",
    "_validated_target_frame",
    "replay_close_targets",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.target_close_replay import (
        _block_frame,
        _daily_record,
        _execution_schedule,
        _exposure_schedule,
        _has_directional_trade_block,
        _has_suspension_conflict,
        _log_holdings,
        _map_targets_to_execution_dates,
        _post_cost_nav,
        _scheduled_target_state,
        _validate_price_calendar,
        _validated_target_frame,
        replay_close_targets,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.target_close_replay")
