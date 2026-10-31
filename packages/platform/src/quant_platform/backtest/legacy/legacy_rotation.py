"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "annotations",
    "build_equal_weight_portfolio",
    "minimize",
    "optimize_portfolio_weights",
    "shrink_covariance_matrix",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.legacy_rotation import (
        annotations,
        build_equal_weight_portfolio,
        minimize,
        optimize_portfolio_weights,
        shrink_covariance_matrix,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.legacy_rotation")
