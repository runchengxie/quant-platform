"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "FACTOR_RETURN_ATTRIBUTION_SCHEMA",
    "FACTOR_RISK_ATTRIBUTION_SCHEMA",
    "FactorReturnAttribution",
    "FactorRiskAttribution",
    "_aligned_inputs",
    "_frame",
    "_series",
    "annotations",
    "attribute_factor_return",
    "attribute_factor_risk",
    "dataclass",
    "isfinite",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.factor_attribution import (
        FACTOR_RETURN_ATTRIBUTION_SCHEMA,
        FACTOR_RISK_ATTRIBUTION_SCHEMA,
        FactorReturnAttribution,
        FactorRiskAttribution,
        _aligned_inputs,
        _frame,
        _series,
        annotations,
        attribute_factor_return,
        attribute_factor_risk,
        dataclass,
        isfinite,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.factor_attribution")
