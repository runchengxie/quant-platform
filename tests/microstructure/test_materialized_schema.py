from __future__ import annotations

from ticknet.eventstream.dataset import N_FEATURES
from ticknet.eventstream.materialized import ARRAY_DTYPES, _array_contract


def test_materialized_array_schema_remains_stable() -> None:
    contract = _array_contract(8)

    assert contract == {
        "x": {"dtype": "float32", "tail_shape": [8, N_FEATURES]},
        "sid": {"dtype": "int16", "tail_shape": [8]},
        "oid": {"dtype": "int16", "tail_shape": [8]},
        "tgt_sid": {"dtype": "int16", "tail_shape": [8]},
        "tgt_oid": {"dtype": "int16", "tail_shape": [8]},
        "tgt_reg": {"dtype": "float32", "tail_shape": [8, 3]},
        "tgt_day": {"dtype": "float32", "tail_shape": []},
        "day_valid": {"dtype": "float32", "tail_shape": []},
        "valid": {"dtype": "float32", "tail_shape": [8]},
        "day": {"dtype": "int64", "tail_shape": []},
    }
    assert set(contract) == set(ARRAY_DTYPES)
