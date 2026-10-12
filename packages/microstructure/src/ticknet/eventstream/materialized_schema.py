"""Array layout contract for materialized eventstream windows."""

from __future__ import annotations

from typing import Any

import numpy as np

from ticknet.eventstream.dataset import N_FEATURES

ARRAY_DTYPES: dict[str, np.dtype[Any]] = {
    "x": np.dtype(np.float32),
    "sid": np.dtype(np.int16),
    "oid": np.dtype(np.int16),
    "tgt_sid": np.dtype(np.int16),
    "tgt_oid": np.dtype(np.int16),
    "tgt_reg": np.dtype(np.float32),
    "tgt_day": np.dtype(np.float32),
    "day_valid": np.dtype(np.float32),
    "valid": np.dtype(np.float32),
    "day": np.dtype(np.int64),
}


def _array_tail_shapes(seq_len: int) -> dict[str, tuple[int, ...]]:
    return {
        "x": (seq_len, N_FEATURES),
        "sid": (seq_len,),
        "oid": (seq_len,),
        "tgt_sid": (seq_len,),
        "tgt_oid": (seq_len,),
        "tgt_reg": (seq_len, 3),
        "tgt_day": (),
        "day_valid": (),
        "valid": (seq_len,),
        "day": (),
    }


def _array_contract(seq_len: int) -> dict[str, dict[str, Any]]:
    tails = _array_tail_shapes(seq_len)
    return {
        name: {"dtype": dtype.name, "tail_shape": list(tails[name])}
        for name, dtype in ARRAY_DTYPES.items()
    }


__all__ = ["ARRAY_DTYPES", "_array_contract", "_array_tail_shapes"]
