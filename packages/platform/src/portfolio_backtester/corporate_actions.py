"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "CorporateAction",
    "Iterable",
    "_action_date",
    "_validate_action_dates",
    "_validate_action_numbers",
    "annotations",
    "dataclass",
    "date",
    "isfinite",
    "normalize_corporate_actions",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.corporate_actions import (
        CorporateAction,
        Iterable,
        _action_date,
        _validate_action_dates,
        _validate_action_numbers,
        annotations,
        dataclass,
        date,
        isfinite,
        normalize_corporate_actions,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.corporate_actions")
