"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "PositionBacktestConfig",
    "PostBufferExposureRepairConfig",
    "_apply_cash_gross_overlay",
    "_apply_post_buffer_exposure_repair",
    "_as_mapping",
    "_auto_bank_industry_breaches",
    "_auto_momentum_breaches",
    "_auto_repair_breaches",
    "_breach_row",
    "_cfg_enabled",
    "_compute_repair_exposure",
    "_exposure_metadata",
    "_first_finite_metric",
    "_first_path_value",
    "_load_table",
    "_repair_config_from_mapping",
    "_repair_exposure_artifacts",
    "_series_from_position_backtest",
    "annotations",
    "apply_position_postprocess",
    "compute_backtest_exposure_analysis",
    "fields",
    "logger",
    "positions_postprocess_enabled",
    "rebuild_backtest_from_positions",
    "repair_post_buffer_exposure",
    "resolve_data_input_path",
    "run_position_backtest",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._position_postprocess_repair import (
        Any,
        Mapping,
        PositionBacktestConfig,
        PostBufferExposureRepairConfig,
        _apply_cash_gross_overlay,
        _apply_post_buffer_exposure_repair,
        _as_mapping,
        _auto_bank_industry_breaches,
        _auto_momentum_breaches,
        _auto_repair_breaches,
        _breach_row,
        _cfg_enabled,
        _compute_repair_exposure,
        _exposure_metadata,
        _first_finite_metric,
        _first_path_value,
        _load_table,
        _repair_config_from_mapping,
        _repair_exposure_artifacts,
        _series_from_position_backtest,
        annotations,
        apply_position_postprocess,
        compute_backtest_exposure_analysis,
        fields,
        logger,
        positions_postprocess_enabled,
        rebuild_backtest_from_positions,
        repair_post_buffer_exposure,
        resolve_data_input_path,
        run_position_backtest,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._position_postprocess_repair")
