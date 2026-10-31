"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "QuotaSleeveSpec",
    "RankBufferedSleeveSpec",
    "SleevePortfolioSpec",
    "_build_position_rows",
    "_eligible_ranked_sleeve_candidate",
    "_exposure_summary",
    "_fill_sleeve",
    "_group_value",
    "_leg_mask",
    "_prepare_signals",
    "_ranked_symbols",
    "_resolve_overlap",
    "_select_quota_sleeve",
    "_select_rank_sleeve",
    "annotations",
    "build_sleeve_positions",
    "cast",
    "compute_position_changes",
    "compute_position_exposure",
    "dataclass",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.sleeve_portfolio import (
        Any,
        Mapping,
        QuotaSleeveSpec,
        RankBufferedSleeveSpec,
        SleevePortfolioSpec,
        _build_position_rows,
        _eligible_ranked_sleeve_candidate,
        _exposure_summary,
        _fill_sleeve,
        _group_value,
        _leg_mask,
        _prepare_signals,
        _ranked_symbols,
        _resolve_overlap,
        _select_quota_sleeve,
        _select_rank_sleeve,
        annotations,
        build_sleeve_positions,
        cast,
        compute_position_changes,
        compute_position_exposure,
        dataclass,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.sleeve_portfolio")
