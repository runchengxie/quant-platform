"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "SelectionSpec",
    "_fractional_seats",
    "_seat_counts",
    "annotations",
    "attach_entry_dates",
    "build_targets",
    "cast",
    "combine_targets",
    "dataclass",
    "select_industry_balanced",
    "target_turnover",
    "validate_targets",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.industry_sleeves import (
        Any,
        Mapping,
        SelectionSpec,
        _fractional_seats,
        _seat_counts,
        annotations,
        attach_entry_dates,
        build_targets,
        cast,
        combine_targets,
        dataclass,
        select_industry_balanced,
        target_turnover,
        validate_targets,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.industry_sleeves")
