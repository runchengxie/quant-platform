"""Frozen feature contract remains causal and preserves historical warm-up filling."""

import importlib
import subprocess
import sys

import numpy as np
import pandas as pd


def panel():
    close = np.linspace(10.0, 30.0, 150)
    return pd.DataFrame(
        {
            "open": close - 0.1,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": 1000.0,
        },
        index=pd.date_range("2020-01-01", periods=150),
    )


def api():
    return importlib.import_module("alpha_research.technical.legacy_features")


def test_features_keep_source_index_and_legacy_warmup_filling():
    data = panel()
    result = api().calculate_technical_features(data)
    assert result.index.equals(data.index)
    assert result["roc_12"].iloc[:12].eq(0.0).all()
    np.testing.assert_allclose(result["roc_12"].iloc[12], (data.close.iloc[12] / 10 - 1) * 100)
    assert "roc_12" not in data


def test_future_prices_do_not_change_past_features():
    data = panel()
    before = api().calculate_technical_features(data)
    data.iloc[140:, data.columns.get_loc("close")] *= 10
    after = api().calculate_technical_features(data)
    pd.testing.assert_frame_equal(before.iloc[:140], after.iloc[:140])


def test_public_entry_remains_importable_when_private_alpha_namespace_shadows():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys, types
sys.modules['alpha_research'] = types.ModuleType('alpha_research')
from quant_platform.legacy_features import calculate_technical_features
import pandas as pd
frame = pd.DataFrame({'open':[10.]*30,'high':[11.]*30,'low':[9.]*30,
                      'close':[10.]*30,'volume':[1000.]*30})
assert len(calculate_technical_features(frame)) == 30
""",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
