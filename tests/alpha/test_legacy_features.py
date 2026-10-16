"""Frozen feature contract remains causal and preserves historical warm-up filling."""

import importlib

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
