"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "Path",
    "_as_mapping",
    "_cfg_enabled",
    "_first_path_value",
    "_load_table",
    "annotations",
    "cast",
    "resolve_data_input_path",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._postprocess_shared import (
        Any,
        Mapping,
        Path,
        _as_mapping,
        _cfg_enabled,
        _first_path_value,
        _load_table,
        annotations,
        cast,
        resolve_data_input_path,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._postprocess_shared")
