"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "TCA_CALIBRATION_SCHEMA",
    "_REQUIRED_COLUMNS",
    "Any",
    "TCACalibrationReceipt",
    "annotations",
    "calibrate_cost_model",
    "dataclass",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.tca_calibration import (
        _REQUIRED_COLUMNS,
        TCA_CALIBRATION_SCHEMA,
        Any,
        TCACalibrationReceipt,
        annotations,
        calibrate_cost_model,
        dataclass,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.tca_calibration")
