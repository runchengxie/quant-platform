"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "PostBufferExposureRepairConfig",
    "PostBufferExposureRepairResult",
    "_apply_momentum_moves",
    "_bank_donors",
    "_bank_pool",
    "_breach_rows",
    "_ensure_symbol",
    "_is_bank_breach",
    "_is_momentum_breach",
    "_momentum_donor_weight",
    "_momentum_pool",
    "_positions_for_date",
    "_prepare_repair_source",
    "_repair_bank",
    "_repair_momentum",
    "_source_for_date",
    "_source_signal",
    "_transfer_weight",
    "add_exposure_momentum_z",
    "annotations",
    "normalize_repair_positions",
    "repair_post_buffer_exposure",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._post_buffer_repair import (
        Any,
        PostBufferExposureRepairConfig,
        PostBufferExposureRepairResult,
        _apply_momentum_moves,
        _bank_donors,
        _bank_pool,
        _breach_rows,
        _ensure_symbol,
        _is_bank_breach,
        _is_momentum_breach,
        _momentum_donor_weight,
        _momentum_pool,
        _positions_for_date,
        _prepare_repair_source,
        _repair_bank,
        _repair_momentum,
        _source_for_date,
        _source_signal,
        _transfer_weight,
        add_exposure_momentum_z,
        annotations,
        normalize_repair_positions,
        repair_post_buffer_exposure,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._post_buffer_repair")
