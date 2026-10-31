"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "MaxNewNamesShortfallPolicy",
    "SelectionConstraints",
    "SelectionPricePolicy",
    "_SelectionInputs",
    "_apply_score_margin_holdover",
    "_build_selection_inputs",
    "_candidate_order_with_score_margin",
    "_fill_buffer_candidates",
    "_initial_buffer_selection",
    "_score_advantage",
    "_select_from_inputs",
    "_selection_group_map",
    "_weakest_new_symbol",
    "annotations",
    "apply_rank_offset",
    "apply_rebalance_buffer",
    "apply_selection_score_threshold",
    "dataclass",
    "entry_amount_values",
    "entry_tradable_flags",
    "ranked_selection_frame",
    "select_candidate_holdings",
    "select_holdings",
    "validate_entry_rank_cutoff",
    "validate_max_new_names_per_rebalance",
    "validate_max_new_names_shortfall_policy",
    "validate_selection_min_score",
    "validate_selection_price_policy",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.portfolio_selection import (
        MaxNewNamesShortfallPolicy,
        SelectionConstraints,
        SelectionPricePolicy,
        _apply_score_margin_holdover,
        _build_selection_inputs,
        _candidate_order_with_score_margin,
        _fill_buffer_candidates,
        _initial_buffer_selection,
        _score_advantage,
        _select_from_inputs,
        _selection_group_map,
        _SelectionInputs,
        _weakest_new_symbol,
        annotations,
        apply_rank_offset,
        apply_rebalance_buffer,
        apply_selection_score_threshold,
        dataclass,
        entry_amount_values,
        entry_tradable_flags,
        ranked_selection_frame,
        select_candidate_holdings,
        select_holdings,
        validate_entry_rank_cutoff,
        validate_max_new_names_per_rebalance,
        validate_max_new_names_shortfall_policy,
        validate_selection_min_score,
        validate_selection_price_policy,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.portfolio_selection")
