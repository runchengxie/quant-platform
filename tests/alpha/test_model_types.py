from __future__ import annotations

from typing import get_args, get_origin, get_type_hints

import numpy as np
from alpha_research.modeling import FixedScoreArtifactModel


def test_fixed_score_model_predict_annotation_is_parameterized() -> None:
    hint = get_type_hints(FixedScoreArtifactModel.predict)["return"]

    assert get_origin(hint) is np.ndarray
    assert len(get_args(hint)) == 2
