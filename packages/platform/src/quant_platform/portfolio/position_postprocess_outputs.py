"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_OUTPUTS",
    "Any",
    "Mapping",
    "Path",
    "annotations",
    "write_position_postprocess_outputs",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.position_postprocess_outputs import (
        _OUTPUTS,
        Any,
        Mapping,
        Path,
        annotations,
        write_position_postprocess_outputs,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.position_postprocess_outputs")
