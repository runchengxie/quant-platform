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


def test_benchmark_score_tilt_accepts_an_arbitrary_score_column() -> None:
    frame = _frame().rename(columns={"ml_score": "fcf_score"})

    weights = build_target_weights(
        frame,
        PortfolioConstructionVariant.BENCHMARK_SCORE_TILT,
        score_col="fcf_score",
        tilt_strength=1.0,
    )

    assert weights["A"] > 0.5
    assert weights["C"] < 0.2
    assert weights.sum() == pytest.approx(1.0)


def test_benchmark_score_tilt_zero_strength_reproduces_benchmark() -> None:
    frame = _frame().rename(columns={"ml_score": "fcf_score"})

    weights = build_target_weights(
        frame, "benchmark_score_tilt", score_col="fcf_score"
    )

    assert weights.tolist() == pytest.approx([0.5, 0.3, 0.2])


def test_legacy_benchmark_ml_tilt_rejects_a_custom_score_column() -> None:
    with pytest.raises(ValueError, match="ml_score"):
        build_target_weights(_frame(), "benchmark_ml_tilt", score_col="other")


def test_variants_validate_only_the_columns_they_consume() -> None:
    topk = _frame().drop(columns=["ml_score", "benchmark_weight"])

    weights = build_target_weights(topk, "topk_equal_weight", top_k=2)

    assert weights.tolist() == pytest.approx([0.5, 0.5])


def test_score_tilt_rejects_invalid_score_column_and_non_finite_values() -> None:
    with pytest.raises(ValueError, match="score_col"):
        build_target_weights(_frame(), "benchmark_score_tilt", score_col="")

    with pytest.raises(ValueError, match="fcf_score"):
        build_target_weights(
            _frame().rename(columns={"ml_score": "fcf_score"})
            .assign(fcf_score=[1.0, np.nan, 0.0]),
            "benchmark_score_tilt",
            score_col="fcf_score",
        )


def test_invalid_input_is_rejected() -> None:
    invalid = _frame().assign(benchmark_weight=[0.5, -0.1, 0.2])

    with pytest.raises(ValueError, match="benchmark_weight"):
        build_target_weights(invalid, "topk_benchmark_weight")


def test_unknown_variant_is_rejected() -> None:
    with pytest.raises(ValueError, match="variant"):
        build_target_weights(_frame(), "unknown")
