"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "PromotionSidecarConfig",
    "_PromotionLedger",
    "_append_fill",
    "_append_order",
    "_append_position_and_cash_state",
    "_append_signal_and_target_events",
    "_append_violation",
    "_build_result",
    "_build_summary",
    "_buy_capacity_and_reason",
    "_empty_result",
    "_format_entry_date",
    "_prepare_positions",
    "_prepare_price_lookup",
    "_price_row",
    "_process_buy_orders",
    "_process_entry_date",
    "_process_sell_orders",
    "_sell_block_reason",
    "annotations",
    "asdict",
    "build_promotion_sidecar_config",
    "cast",
    "dataclass",
    "promotion_sidecar_config_from_pipeline_config",
    "simulate_promotion_sidecar",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.promotion_sidecar import (
        Any,
        Mapping,
        PromotionSidecarConfig,
        _append_fill,
        _append_order,
        _append_position_and_cash_state,
        _append_signal_and_target_events,
        _append_violation,
        _build_result,
        _build_summary,
        _buy_capacity_and_reason,
        _empty_result,
        _format_entry_date,
        _prepare_positions,
        _prepare_price_lookup,
        _price_row,
        _process_buy_orders,
        _process_entry_date,
        _process_sell_orders,
        _PromotionLedger,
        _sell_block_reason,
        annotations,
        asdict,
        build_promotion_sidecar_config,
        cast,
        dataclass,
        promotion_sidecar_config_from_pipeline_config,
        simulate_promotion_sidecar,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.promotion_sidecar")
