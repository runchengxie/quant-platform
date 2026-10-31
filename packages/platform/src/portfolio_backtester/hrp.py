"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Callable",
    "HrpConfig",
    "HrpResult",
    "_apply_bounds",
    "_cluster_variance",
    "_covariance_to_correlation",
    "_recursive_bisection",
    "_shrink_covariance",
    "annotations",
    "asdict",
    "cluster_stability",
    "dataclass",
    "hierarchical_risk_parity",
    "pairwise",
    "rolling_hrp_weights",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.hrp import (
        Callable,
        HrpConfig,
        HrpResult,
        _apply_bounds,
        _cluster_variance,
        _covariance_to_correlation,
        _recursive_bisection,
        _shrink_covariance,
        annotations,
        asdict,
        cluster_stability,
        dataclass,
        hierarchical_risk_parity,
        pairwise,
        rolling_hrp_weights,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.hrp")
