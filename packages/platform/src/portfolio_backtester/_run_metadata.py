"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_GIT_REF_ENV",
    "Any",
    "Mapping",
    "Path",
    "_config_version_field",
    "_dependency_versions",
    "_normalize_payload",
    "_repo_commit",
    "annotations",
    "collect_reproducibility",
    "datetime",
    "sha256_file",
    "write_receipt",
    "write_run_metadata",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._run_metadata import (
        _GIT_REF_ENV,
        Any,
        Mapping,
        Path,
        _config_version_field,
        _dependency_versions,
        _normalize_payload,
        _repo_commit,
        annotations,
        collect_reproducibility,
        datetime,
        sha256_file,
        write_receipt,
        write_run_metadata,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._run_metadata")
