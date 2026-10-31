"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DATA_PLATFORM_PATH_PREFIXES",
    "DEFAULT_SYMBOL_PRIORITY",
    "ENV_DATA_PLATFORM_ROOT",
    "ENV_HK_DATA_PLATFORM_ROOT",
    "LEGACY_SYMBOL_COLUMNS",
    "SYMBOL_COL",
    "Path",
    "Sequence",
    "_clean_symbol_series",
    "_column_series",
    "_configured_data_input_path",
    "_data_platform_relative_path",
    "_drop_legacy_symbol_columns",
    "_ensure_symbol_columns",
    "_normalize_path_text",
    "_resolve_artifacts_root",
    "_resolve_env_path",
    "_resolve_hk_data_platform_root",
    "_resolve_repo_path",
    "_resolve_symbol_series",
    "canonicalize_symbol_columns",
    "resolve_data_input_path",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._symbol_utils import (
        DATA_PLATFORM_PATH_PREFIXES,
        DEFAULT_SYMBOL_PRIORITY,
        ENV_DATA_PLATFORM_ROOT,
        ENV_HK_DATA_PLATFORM_ROOT,
        LEGACY_SYMBOL_COLUMNS,
        SYMBOL_COL,
        Path,
        Sequence,
        _clean_symbol_series,
        _column_series,
        _configured_data_input_path,
        _data_platform_relative_path,
        _drop_legacy_symbol_columns,
        _ensure_symbol_columns,
        _normalize_path_text,
        _resolve_artifacts_root,
        _resolve_env_path,
        _resolve_hk_data_platform_root,
        _resolve_repo_path,
        _resolve_symbol_series,
        canonicalize_symbol_columns,
        resolve_data_input_path,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._symbol_utils")
