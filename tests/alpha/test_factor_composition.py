"""Composition regressions use hand-derived cross-sections, not strategy data."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from alpha_research.factor_composition import (
    FactorCompositionSpec,
    FactorInput,
    compose_factors,
)


def panel():
    index = pd.MultiIndex.from_product(
        [pd.date_range("2026-01-01", periods=2), ["A", "B", "C", "D"]],
        names=["date", "symbol"],
    )
    return pd.DataFrame({"Q": [1.0, 2.0, 3.0, 4.0] * 2, "V": [4.0, 2.0, 3.0, 1.0] * 2}, index=index)


def spec(method="equal", **kwargs):
    return FactorCompositionSpec(
        composition_id="example",
        version="v1",
        inputs=(FactorInput("Q", "quality", "v1"), FactorInput("V", "value", "v2")),
        method=method,
        normalization="none",
        **kwargs,
    )


def test_equal_and_signed_weighted_scores_preserve_input():
    frame = panel()
    before = frame.copy()
    result = compose_factors(frame, spec())
    np.testing.assert_allclose(result.scores.iloc[:4], [2.5, 2.0, 3.0, 2.5])
    weighted = compose_factors(frame, spec("weighted", weights={"Q": 0.8, "V": 0.2}))
    np.testing.assert_allclose(weighted.scores.iloc[:4], [1.6, 2.0, 3.0, 3.4])
    pd.testing.assert_frame_equal(before, frame)
    reversed_spec = replace(
        spec(), inputs=(FactorInput("Q", "quality", "v1", -1), FactorInput("V", "value", "v2"))
    )
    np.testing.assert_allclose(
        compose_factors(frame, reversed_spec).scores.iloc[:4], [1.5, 0.0, 0.0, -1.5]
    )


def test_mapping_is_strict_fingerprinted_and_roundtrips():
    original = spec("weighted", weights={"Q": 0.8, "V": 0.2})
    assert (
        FactorCompositionSpec.from_mapping(original.to_mapping()).fingerprint
        == original.fingerprint
    )
    assert replace(original, version="v2").fingerprint != original.fingerprint
    with pytest.raises(ValueError, match="unknown"):
        FactorCompositionSpec.from_mapping({**original.to_mapping(), "typo": True})
    with pytest.raises(ValueError):
        spec("weighted", weights={"Q": float("nan"), "V": 1.0})
    with pytest.raises(ValueError):
        replace(spec(), inputs=())


@pytest.mark.parametrize(
    "method,options",
    [
        ("unknown", {}),
        ("weighted", {"weights": {"Q": 1}}),
        ("hierarchical", {"groups": {"quality": ["Q"], "other": ["Q", "V"]}}),
        ("residualized", {"residualize": {"Q": ["Q"]}}),
        ("interaction", {"interactions": [("Q", "oops", 0.2)]}),
    ],
)
def test_invalid_configuration_fails_before_calculation(method, options):
    with pytest.raises(ValueError):
        spec(method, **options)


def test_missing_policy_does_not_silently_renormalize_or_zero():
    frame = panel()
    frame.iloc[0, 0] = np.nan
    assert np.isnan(compose_factors(frame, spec()).scores.iloc[0])
    with pytest.raises(ValueError, match="missing"):
        compose_factors(frame, spec(missing_policy="error"))
    frame.iloc[0, 0] = np.inf
    with pytest.raises(ValueError, match="finite"):
        compose_factors(frame, spec())


def test_zscore_is_per_date_constant_columns_produce_zero():
    frame = panel()
    frame.loc[pd.IndexSlice[pd.Timestamp("2026-01-02"), :], "Q"] = 100.0
    result = compose_factors(frame, replace(spec(), normalization="zscore"))
    assert result.transformed.loc["2026-01-01", "Q"].mean() == pytest.approx(0.0)
    np.testing.assert_allclose(result.transformed.loc["2026-01-02", "Q"], 0.0)
    ranked = compose_factors(panel(), spec("rank"))
    np.testing.assert_allclose(ranked.scores.iloc[:4], [0.625, 0.5, 0.75, 0.625])


def test_hierarchy_weights_groups_equally_and_residual_is_orthogonal():
    frame = panel().assign(Q2=lambda x: x.Q)
    hierarchical = FactorCompositionSpec(
        "grouped",
        "v1",
        (*spec().inputs, FactorInput("Q2", "q2", "v1")),
        method="hierarchical",
        normalization="none",
        groups={"quality": ["Q", "Q2"], "value": ["V"]},
    )
    np.testing.assert_allclose(
        compose_factors(frame, hierarchical).scores.iloc[:4], [2.5, 2.0, 3.0, 2.5]
    )
    residual = compose_factors(panel(), spec("residualized", residualize={"V": ["Q"]}))
    r = residual.transformed.loc["2026-01-01", "V"]
    assert r.mean() == pytest.approx(0.0, abs=1e-12)
    assert np.dot(r, [1.0, 2.0, 3.0, 4.0]) == pytest.approx(0.0, abs=1e-12)


def test_interaction_keeps_main_effects_and_conditional_uses_gate():
    result = compose_factors(
        panel(), spec("interaction", weights={"Q": 0.4, "V": 0.4}, interactions=[("Q", "V", 0.2)])
    )
    np.testing.assert_allclose(result.scores.iloc[:4], [2.8, 2.4, 4.2, 2.8])
    conditional = compose_factors(
        panel(),
        spec(
            "conditional",
            gate="Q",
            threshold=2.0,
            weights={"Q": 0.0, "V": 1.0},
            low_weights={"Q": 1.0, "V": 0.0},
        ),
    )
    np.testing.assert_allclose(conditional.scores.iloc[:4], [1.0, 2.0, 3.0, 1.0])


def test_duplicate_rows_bad_dates_and_singular_residualization_fail_closed():
    frame = panel()
    with pytest.raises(ValueError, match="unique"):
        compose_factors(pd.concat([frame, frame.iloc[:1]]), spec())
    frame.index = pd.MultiIndex.from_product(
        [["bad", "date"], list("ABCD")], names=["date", "symbol"]
    )
    with pytest.raises(ValueError, match="date"):
        compose_factors(frame, spec())
    with pytest.raises(ValueError, match="rank"):
        compose_factors(panel().assign(Q=1.0), spec("residualized", residualize={"V": ["Q"]}))


def test_composite_can_register_in_existing_factor_catalog_without_a_second_identity():
    from alpha_research.factor_catalog import FactorCatalog

    result = compose_factors(panel(), spec())
    identity = result.to_factor_spec(
        owner="example",
        frequency="daily",
        pit_semantics="caller_aligned",
        universe_semantics="synthetic",
        implementation_sha256="a" * 64,
    )
    catalog = FactorCatalog()
    catalog.register(identity)
    assert catalog.get(("example", "v1")).dependencies == ("quality@v1", "value@v2")
    assert result.fingerprint in identity.description


def test_complex_factor_values_are_rejected_instead_of_discarded():
    with pytest.raises(ValueError, match="real"):
        compose_factors(panel().astype(complex) + 10j, spec())


def test_input_fingerprint_covers_schema_as_well_as_values():
    from alpha_research.factor_composition import composition_frame_sha256

    frame = panel()
    assert composition_frame_sha256(frame) != composition_frame_sha256(
        frame.rename(columns={"Q": "X"})
    )
    assert composition_frame_sha256(frame) != composition_frame_sha256(frame.astype("float32"))


def test_overflowing_scores_fail_instead_of_becoming_valid_signals():
    with pytest.raises(ValueError, match="finite"):
        compose_factors(panel(), spec("weighted", weights={"Q": 1e308, "V": 1e308}))


def test_rank_catalog_records_effective_normalization():
    result = compose_factors(panel(), replace(spec("rank"), normalization="zscore"))
    identity = result.to_factor_spec(
        owner="example",
        frequency="daily",
        pit_semantics="caller_aligned",
        universe_semantics="synthetic",
        implementation_sha256="a" * 64,
    )
    assert "normalization:rank" in identity.preprocessing
