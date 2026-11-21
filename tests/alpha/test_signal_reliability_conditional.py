"""Synthetic attribution and paired-model evidence, never causal claims."""

import numpy as np
import pandas as pd
import pytest
from alpha_research import signal_reliability as sr


def sample(correlated=True):
    rng = np.random.default_rng(98)
    rows = []
    for date in pd.date_range("2020-01-01", periods=10):
        control = rng.normal(size=200)
        factor = (control if correlated else 0) + rng.normal(scale=0.4, size=200)
        ret = 0.02 * factor - 0.06 * control + rng.normal(scale=0.001, size=200)
        rows.extend(
            {
                "trade_date": date,
                "symbol": str(i),
                "factor": factor[i],
                "control": control[i],
                "ret": ret[i],
                "industry": str(i % 3),
            }
            for i in range(200)
        )
    return pd.DataFrame(rows)


def opts():
    return {
        "factor_cols": ("factor",),
        "target_col": "ret",
        "control_cols": ("control",),
        "min_obs": 30,
        "ks": (10,),
        "statistics": sr.BlockStatistics(block_length=2, repetitions=100, min_dates=5),
    }


def test_confounding_raw_sign_reverses_but_conditional_coefficient_stays_positive():
    result = sr.conditional_factor_profile(sample(), **opts())
    rows = result.profile.set_index("metric")
    assert rows.loc["raw_rank_ic", "mean"] < -0.7
    assert rows.loc["partial_rank_ic", "mean"] > 0.6
    assert rows.loc["conditional_coefficient", "mean"] > 0.018
    assert result.summary["incremental_status"] == "not_provided"


def test_independent_noise_and_industry_controls_preserve_positive_relation():
    data = sample(False)
    result = sr.conditional_factor_profile(data, **(opts() | {"industry_col": "industry"}))
    coef = result.by_date.query("metric == 'conditional_coefficient'")
    assert set(coef.status) == {"ok"}
    # Per factor standard deviation: 0.02 * 0.4 ~= 0.008.
    assert coef.value.mean() == pytest.approx(0.008, abs=0.001)
    assert (coef.design_rank == 5).all()


def test_missing_controls_share_sample_and_missing_industry_is_not_a_category():
    data = sample()
    data.loc[data.symbol == "0", "control"] = np.nan
    data.loc[data.symbol == "1", "industry"] = None
    result = sr.conditional_factor_profile(data, **(opts() | {"industry_col": "industry"}))
    raw = result.by_date.query("metric == 'raw_rank_ic'")
    full = result.by_date.query("metric == 'raw_full_rank_ic'")
    assert set(raw.n_obs) == {198}
    assert set(full.n_obs) == {200}


@pytest.mark.parametrize("kind", ["collinear", "constant", "duplicate_control"])
def test_unidentified_design_does_not_invent_an_effect(kind):
    data = sample()
    kwargs = opts()
    if kind == "collinear":
        data["factor"] = data.control
    elif kind == "constant":
        data["factor"] = 1.0
    else:
        data["control2"] = data.control
        kwargs["control_cols"] = ("control", "control2")
    result = sr.conditional_factor_profile(data, **kwargs)
    controlled = result.by_date[
        result.by_date.metric.isin(["partial_rank_ic", "conditional_coefficient"])
    ]
    assert controlled.value.isna().all()
    assert set(controlled.status) == {"unidentified"}


def provenance():
    identity = {
        "label_id": "ret-v1",
        "universe_id": "pool-v1",
        "split_id": "oos-v1",
        "prediction_availability": "before_label_start",
    }
    return {
        "baseline": identity | {"run_id": "base"},
        "augmented": identity | {"run_id": "add-factor"},
        "feature_change": "add factor",
    }


def test_paired_model_gain_uses_common_prediction_universe():
    data = sample()
    data["baseline"] = -data.ret
    data["augmented"] = data.ret
    data.loc[data.symbol == "0", "baseline"] = np.nan
    result = sr.conditional_factor_profile(
        data,
        **opts(),
        baseline_col="baseline",
        augmented_col="augmented",
        paired_provenance=provenance(),
    )
    row = result.profile.query("metric == 'rank_ic_delta'").iloc[0]
    assert row["mean"] == pytest.approx(2)
    paired = result.by_date.query("metric == 'rank_ic_delta'")
    assert set(paired.n_prediction_pairs) == {199}
    assert set(paired.n_universe) == {200}
    assert result.summary["incremental_status"] == "provided_declared_oos"


def test_paired_missing_labels_are_not_backfilled():
    data = sample()
    data["baseline"] = data.symbol.astype(int)
    data["augmented"] = -data.baseline
    data.loc[data.symbol == "0", "ret"] = np.nan
    result = sr.conditional_factor_profile(
        data,
        **opts(),
        baseline_col="baseline",
        augmented_col="augmented",
        paired_provenance=provenance(),
    )
    rows = result.by_date.query("metric == 'top_return_delta'")
    assert rows.value.isna().all()
    assert set(rows.status) == {"missing_labels"}


@pytest.mark.parametrize("kind", ["missing", "mismatch", "single_column"])
def test_incremental_evidence_requires_compatible_declared_identity(kind):
    data = sample().assign(baseline=1, augmented=2)
    meta = provenance()
    kwargs = {"baseline_col": "baseline", "augmented_col": "augmented", "paired_provenance": meta}
    if kind == "missing":
        meta["baseline"].pop("run_id")
    elif kind == "mismatch":
        meta["augmented"]["split_id"] = "other"
    else:
        kwargs.pop("augmented_col")
    with pytest.raises(ValueError):
        sr.conditional_factor_profile(data, **opts(), **kwargs)


def test_no_controls_reports_not_requested_and_raw_evidence():
    result = sr.conditional_factor_profile(sample(), **(opts() | {"control_cols": ()}))
    controlled = result.by_date.query("metric == 'partial_rank_ic'")
    assert set(controlled.status) == {"not_requested"}
    assert controlled.value.isna().all()


@pytest.mark.parametrize("description", [None, [], {}, 42, " "])
def test_paired_feature_change_must_be_a_nonblank_string(description):
    data = sample().assign(baseline=1, augmented=2)
    meta = provenance()
    meta["feature_change"] = description
    with pytest.raises(ValueError, match="feature change"):
        sr.conditional_factor_profile(
            data,
            **opts(),
            baseline_col="baseline",
            augmented_col="augmented",
            paired_provenance=meta,
        )
