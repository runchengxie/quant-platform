from __future__ import annotations

from typing import get_args, get_origin, get_type_hints

import numpy as np
from alpha_research._split_windows import _time_decay_weights


def test_time_decay_weight_annotation_is_parameterized() -> None:
    return_hint = get_type_hints(_time_decay_weights)["return"]

    arrays = [item for item in get_args(return_hint) if get_origin(item) is np.ndarray]

    assert len(arrays) == 1
    assert len(get_args(arrays[0])) == 2
