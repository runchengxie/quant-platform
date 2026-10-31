"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA",
    "Any",
    "EqualWeightOptimizerBackend",
    "HrpConfig",
    "HrpOptimizerBackend",
    "InverseVolConfig",
    "InverseVolOptimizerBackend",
    "LinearExposureConstraint",
    "Mapping",
    "OptimizerRegistry",
    "PortfolioOptimizationRequest",
    "PortfolioOptimizationResult",
    "PortfolioOptimizerBackend",
    "PortfolioQpConfig",
    "Protocol",
    "QpMinVarianceOptimizerBackend",
    "_numeric_series_for_assets",
    "_project_weights_to_bounds",
    "_qp_constraint_residuals",
    "_qp_constraints",
    "_qp_covariance",
    "_qp_objective",
    "_qp_solution_weights",
    "_validate_json_scalars",
    "annotations",
    "dataclass",
    "field",
    "hierarchical_risk_parity",
    "isfinite",
    "runtime_checkable",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.optimization import (
        PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA,
        Any,
        EqualWeightOptimizerBackend,
        HrpConfig,
        HrpOptimizerBackend,
        InverseVolConfig,
        InverseVolOptimizerBackend,
        LinearExposureConstraint,
        Mapping,
        OptimizerRegistry,
        PortfolioOptimizationRequest,
        PortfolioOptimizationResult,
        PortfolioOptimizerBackend,
        PortfolioQpConfig,
        Protocol,
        QpMinVarianceOptimizerBackend,
        _numeric_series_for_assets,
        _project_weights_to_bounds,
        _qp_constraint_residuals,
        _qp_constraints,
        _qp_covariance,
        _qp_objective,
        _qp_solution_weights,
        _validate_json_scalars,
        annotations,
        dataclass,
        field,
        hierarchical_risk_parity,
        isfinite,
        runtime_checkable,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.optimization")
