"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "FloatVector",
    "Sequence",
    "_finite_vector",
    "_uncertainty_vector",
    "add_conservative_score",
    "annotations",
    "box_worst_case_return",
    "conservative_score",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.robust_uncertainty import (
        FloatVector,
        Sequence,
        _finite_vector,
        _uncertainty_vector,
        add_conservative_score,
        annotations,
        box_worst_case_return,
        conservative_score,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.robust_uncertainty")
