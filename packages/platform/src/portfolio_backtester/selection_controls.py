"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Literal",
    "MaxNewNamesShortfallPolicy",
    "SelectionConstraints",
    "SelectionPricePolicy",
    "TargetWeightPolicy",
    "annotations",
    "apply_liquidity_floor_to_day",
    "apply_selection_score_threshold",
    "cast",
    "controlled_selection_day",
    "entry_amount_values",
    "entry_tradable_flags",
    "merge_pricing_supplemental_columns",
    "ranked_selection_frame",
    "validate_entry_rank_cutoff",
    "validate_max_new_names_per_rebalance",
    "validate_max_new_names_shortfall_policy",
    "validate_max_positive_names",
    "validate_selection_min_score",
    "validate_selection_price_policy",
    "validate_target_weight_policy",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.selection_controls import (
        Any,
        Literal,
        MaxNewNamesShortfallPolicy,
        SelectionConstraints,
        SelectionPricePolicy,
        TargetWeightPolicy,
        annotations,
        apply_liquidity_floor_to_day,
        apply_selection_score_threshold,
        cast,
        controlled_selection_day,
        entry_amount_values,
        entry_tradable_flags,
        merge_pricing_supplemental_columns,
        ranked_selection_frame,
        validate_entry_rank_cutoff,
        validate_max_new_names_per_rebalance,
        validate_max_new_names_shortfall_policy,
        validate_max_positive_names,
        validate_selection_min_score,
        validate_selection_price_policy,
        validate_target_weight_policy,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.selection_controls")
