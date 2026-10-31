"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "Path",
    "annotations",
    "build_portfolio_sizing_receipt",
    "series_sha256",
    "sha256_file",
    "write_receipt",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.evidence_receipts import (
        Any,
        Mapping,
        Path,
        annotations,
        build_portfolio_sizing_receipt,
        series_sha256,
        sha256_file,
        write_receipt,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.evidence_receipts")
