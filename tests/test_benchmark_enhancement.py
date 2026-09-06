import numpy as np
import pandas as pd
import pytest

from portfolio_backtester.benchmark_enhancement import (
    PortfolioConstructionVariant,
    build_target_weights,
)


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "symbol": ["B", "A", "C"],
            "selection_rank": [2, 1, 3],
            "ml_score": [0.0, 1.0, -1.0],
            "benchmark_weight": [0.3, 0.5, 0.2],
        }
    )


def test_topk_equal_weight_is_ranked_and_sums_to_one() -> None:
    weights = build_target_weights(_frame(), "topk_equal_weight", top_k=2)

    assert weights.index.tolist() == ["A", "B"]
    assert weights.tolist() == pytest.approx([0.5, 0.5])


def test_topk_benchmark_weight_renormalizes_selected_benchmark() -> None:
    weights = build_target_weights(
        _frame(), PortfolioConstructionVariant.TOPK_BENCHMARK_WEIGHT, top_k=2
    )

    assert weights["A"] == pytest.approx(0.5 / 0.8)
    assert weights["B"] == pytest.approx(0.3 / 0.8)
    assert weights.sum() == pytest.approx(1.0)


def test_benchmark_ml_tilt_zero_strength_reproduces_benchmark() -> None:
    weights = build_target_weights(_frame(), "benchmark_ml_tilt", tilt_strength=0.0)

    assert weights.index.tolist() == ["A", "B", "C"]
    assert weights.tolist() == pytest.approx([0.5, 0.3, 0.2])


def test_benchmark_ml_tilt_overweights_high_score() -> None:
    weights = build_target_weights(_frame(), "benchmark_ml_tilt", tilt_strength=1.0)

    assert weights["A"] > 0.5
    assert weights["C"] < 0.2
    assert np.isclose(weights.sum(), 1.0)


def test_invalid_input_is_rejected() -> None:
    invalid = _frame().assign(benchmark_weight=[0.5, -0.1, 0.2])

    with pytest.raises(ValueError, match="benchmark_weight"):
        build_target_weights(invalid, "topk_equal_weight")


def test_unknown_variant_is_rejected() -> None:
    with pytest.raises(ValueError, match="variant"):
        build_target_weights(_frame(), "unknown")
