"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_EXPOSURE_INDEX_NAMES",
    "_RETURN_COLUMN",
    "FactorReturnResult",
    "Final",
    "PortfolioRiskAttribution",
    "RiskModelConfig",
    "RiskModelResult",
    "_as_return_series",
    "_ewma_weights",
    "_nearest_psd",
    "_prepare_attribution_inputs",
    "_snapshot_exposures",
    "_validate_estimation_weights",
    "_validate_exposure_frame",
    "_weighted_covariance",
    "_weighted_regression",
    "annotations",
    "attribute_portfolio_risk",
    "build_risk_model",
    "dataclass",
    "estimate_factor_returns",
    "validate_risk_inputs",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.risk_model import (
        _EXPOSURE_INDEX_NAMES,
        _RETURN_COLUMN,
        FactorReturnResult,
        Final,
        PortfolioRiskAttribution,
        RiskModelConfig,
        RiskModelResult,
        _as_return_series,
        _ewma_weights,
        _nearest_psd,
        _prepare_attribution_inputs,
        _snapshot_exposures,
        _validate_estimation_weights,
        _validate_exposure_frame,
        _weighted_covariance,
        _weighted_regression,
        annotations,
        attribute_portfolio_risk,
        build_risk_model,
        dataclass,
        estimate_factor_returns,
        validate_risk_inputs,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.risk_model")
