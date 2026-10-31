"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "TCA_EVIDENCE_SCHEMA",
    "_NUMERIC",
    "Any",
    "Path",
    "Sequence",
    "_checksum",
    "_mean_interval",
    "_summarize_group",
    "_validated_observations",
    "annotations",
    "read_tca_evidence",
    "summarize_tca",
    "validate_tca_evidence",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.tca_evidence import (
        _NUMERIC,
        TCA_EVIDENCE_SCHEMA,
        Any,
        Path,
        Sequence,
        _checksum,
        _mean_interval,
        _summarize_group,
        _validated_observations,
        annotations,
        read_tca_evidence,
        summarize_tca,
        validate_tca_evidence,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.tca_evidence")
