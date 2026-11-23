"""Schema-aware input identities for composition and private experiment consumers."""

from __future__ import annotations

import hashlib
import json

import pandas as pd


def composition_frame_sha256(frame: pd.DataFrame) -> str:
    """Hash ordered values, column identities/dtypes and index names/dtypes."""
    schema = {
        "columns": [
            (type(name).__name__, str(name), str(dtype))
            for name, dtype in zip(frame.columns, frame.dtypes, strict=True)
        ],
        "index": [
            (str(name), str(frame.index.get_level_values(level).dtype))
            for level, name in enumerate(frame.index.names)
        ],
    }
    digest = hashlib.sha256(json.dumps(schema, sort_keys=True, separators=(",", ":")).encode())
    digest.update(pd.util.hash_pandas_object(frame, index=True).values.tobytes())
    return digest.hexdigest()
