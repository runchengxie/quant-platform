"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_BASE_COLUMNS",
    "_REQUIRED_COLUMNS",
    "PortfolioConstructionVariant",
    "StrEnum",
    "_topk",
    "_validated_frame",
    "annotations",
    "build_target_weights",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.benchmark_enhancement import (
        _BASE_COLUMNS,
        _REQUIRED_COLUMNS,
        PortfolioConstructionVariant,
        StrEnum,
        _topk,
        _validated_frame,
        annotations,
        build_target_weights,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.benchmark_enhancement")
