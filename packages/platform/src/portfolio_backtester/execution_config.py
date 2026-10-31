"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "BpsCostModel",
    "Mapping",
    "_merge_execution_config",
    "annotations",
    "build_execution_model",
    "build_execution_sim_config",
    "required_execution_sim_columns",
    "required_pricing_columns",
    "resolve_execution_settings",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_config import (
        Any,
        BpsCostModel,
        Mapping,
        _merge_execution_config,
        annotations,
        build_execution_model,
        build_execution_sim_config,
        required_execution_sim_columns,
        required_pricing_columns,
        resolve_execution_settings,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_config")
