"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "CANONICAL_POSITIONS_BY_REBALANCE_FILE",
    "CANONICAL_POSITIONS_BY_REBALANCE_META_FILE",
    "POSITIONS_BY_REBALANCE_CONTRACT_NAME",
    "POSITIONS_BY_REBALANCE_REQUIRED_COLUMNS",
    "POSITIONS_BY_REBALANCE_SCHEMA_VERSION",
    "PRODUCER_BACKEND",
    "PRODUCER_REPOSITORY",
    "UTC",
    "Any",
    "ArtifactEnvelopeV2",
    "LineageInput",
    "Mapping",
    "PackageNotFoundError",
    "Path",
    "ProducerIdentity",
    "Sequence",
    "_git_commit",
    "_producer_version",
    "annotations",
    "assert_positions_by_rebalance_frame",
    "attach_artifact_envelope_v2",
    "build_positions_envelope_v2",
    "canonical_json_sha256",
    "datetime",
    "file_sha256",
    "package_version",
    "write_positions_by_rebalance_artifact",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.positions_artifact import (
        CANONICAL_POSITIONS_BY_REBALANCE_FILE,
        CANONICAL_POSITIONS_BY_REBALANCE_META_FILE,
        POSITIONS_BY_REBALANCE_CONTRACT_NAME,
        POSITIONS_BY_REBALANCE_REQUIRED_COLUMNS,
        POSITIONS_BY_REBALANCE_SCHEMA_VERSION,
        PRODUCER_BACKEND,
        PRODUCER_REPOSITORY,
        UTC,
        Any,
        ArtifactEnvelopeV2,
        LineageInput,
        Mapping,
        PackageNotFoundError,
        Path,
        ProducerIdentity,
        Sequence,
        _git_commit,
        _producer_version,
        annotations,
        assert_positions_by_rebalance_frame,
        attach_artifact_envelope_v2,
        build_positions_envelope_v2,
        canonical_json_sha256,
        datetime,
        file_sha256,
        package_version,
        write_positions_by_rebalance_artifact,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.positions_artifact")
