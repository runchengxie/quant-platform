from __future__ import annotations

from typing import get_args, get_origin, get_type_hints

import numpy as np
from alpha_research._split_cv import _purged_cv_train_indices


def test_purged_cv_indices_annotation_is_parameterized() -> None:
    hint = get_type_hints(_purged_cv_train_indices)["return"]
    arrays = [item for item in get_args(hint) if get_origin(item) is np.ndarray]

    assert len(arrays) == 1
    assert len(get_args(arrays[0])) == 2
