"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "TYPE_CHECKING",
    "_EULER_GAMMA",
    "_SQRT_TWO",
    "_acklam_ppf",
    "annotations",
    "annualized_sharpe_to_periodic",
    "annualized_variance_to_periodic",
    "deflated_sharpe_ratio",
    "expected_max_sharpe",
    "norm_cdf",
    "norm_ppf",
    "probabilistic_sharpe_ratio",
    "sharpe_standard_error",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.sharpe_inference import (
        _EULER_GAMMA,
        _SQRT_TWO,
        TYPE_CHECKING,
        _acklam_ppf,
        annotations,
        annualized_sharpe_to_periodic,
        annualized_variance_to_periodic,
        deflated_sharpe_ratio,
        expected_max_sharpe,
        norm_cdf,
        norm_ppf,
        probabilistic_sharpe_ratio,
        sharpe_standard_error,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.sharpe_inference")
