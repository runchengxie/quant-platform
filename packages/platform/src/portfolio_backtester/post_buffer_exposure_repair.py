"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "MOMENTUM_COLUMNS",
    "PostBufferExposureRepairConfig",
    "PostBufferExposureRepairResult",
    "add_exposure_momentum_z",
    "annotations",
    "normalize_repair_positions",
    "repair_post_buffer_exposure",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.post_buffer_exposure_repair import (
        MOMENTUM_COLUMNS,
        PostBufferExposureRepairConfig,
        PostBufferExposureRepairResult,
        add_exposure_momentum_z,
        annotations,
        normalize_repair_positions,
        repair_post_buffer_exposure,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.post_buffer_exposure_repair")
