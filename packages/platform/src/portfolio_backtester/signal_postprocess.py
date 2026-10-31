"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Sequence",
    "annotations",
    "apply_score_postprocess",
    "apply_score_postprocess_inplace",
    "neutralize_cross_sectional_series",
    "rank_blend_cross_sectional_series",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.signal_postprocess import (
        Sequence,
        annotations,
        apply_score_postprocess,
        apply_score_postprocess_inplace,
        neutralize_cross_sectional_series,
        rank_blend_cross_sectional_series,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.signal_postprocess")
