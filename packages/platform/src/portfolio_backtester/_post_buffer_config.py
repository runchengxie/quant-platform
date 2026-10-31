"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "MOMENTUM_COLUMNS",
    "Any",
    "PostBufferExposureRepairConfig",
    "PostBufferExposureRepairResult",
    "_breach_rows",
    "_compact_date_series",
    "_is_bank_breach",
    "_is_momentum_breach",
    "_prepare_repair_source",
    "_zscore",
    "add_exposure_momentum_z",
    "annotations",
    "dataclass",
    "normalize_repair_positions",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._post_buffer_config import (
        MOMENTUM_COLUMNS,
        Any,
        PostBufferExposureRepairConfig,
        PostBufferExposureRepairResult,
        _breach_rows,
        _compact_date_series,
        _is_bank_breach,
        _is_momentum_breach,
        _prepare_repair_source,
        _zscore,
        add_exposure_momentum_z,
        annotations,
        dataclass,
        normalize_repair_positions,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._post_buffer_config")
