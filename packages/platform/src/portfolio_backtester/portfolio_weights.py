"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_WEIGHTING_MODES",
    "SizingConfig",
    "TargetWeightPolicy",
    "_apply_target_weight_policy",
    "_calibrated_weights",
    "_cap_and_redistribute_positive_weights",
    "_equal_weights",
    "_score_weights",
    "_sqrt_liquidity_weights",
    "_weights_for_mode",
    "annotations",
    "build_position_weights",
    "build_sized_weights",
    "clean_position_weights",
    "limit_weight_turnover",
    "normalize_position_weights",
    "normalize_weighting_mode",
    "validate_positive_name_invariant",
    "validate_target_weight_policy",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.portfolio_weights import (
        _WEIGHTING_MODES,
        SizingConfig,
        TargetWeightPolicy,
        _apply_target_weight_policy,
        _calibrated_weights,
        _cap_and_redistribute_positive_weights,
        _equal_weights,
        _score_weights,
        _sqrt_liquidity_weights,
        _weights_for_mode,
        annotations,
        build_position_weights,
        build_sized_weights,
        clean_position_weights,
        limit_weight_turnover,
        normalize_position_weights,
        normalize_weighting_mode,
        validate_positive_name_invariant,
        validate_target_weight_policy,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.portfolio_weights")
