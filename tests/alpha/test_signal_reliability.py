"""Selection and uncertainty contracts; returns are hand-derived."""

import numpy as np
import pandas as pd
import pytest
from alpha_research import signal_reliability as sr


def panel(returns=(0.08, 0.06, 0.04, 0.02), dates=8):
    return pd.DataFrame(
        [
            {"date": date, "symbol": str(i), "score": 10 - i, "ret": ret}
            for date in pd.date_range("2020-01-01", periods=dates)
            for i, ret in enumerate(returns)
        ]
    )


def options():
    return {
        "date_col": "date",
        "score_col": "score",
        "target_col": "ret",
        "ks": (1, 2),
        "statistics": sr.BlockStatistics(block_length=2, repetitions=100, min_dates=4, seed=17),
    }


def test_equal_weight_bands_and_paired_margins():
    result = sr.tail_return_profile(panel(), **options())
    first = result.by_date.iloc[:4].set_index("group")
    assert first.loc["band:1:1", "value"] == pytest.approx(0.08)
    assert first.loc["band:2:2", "value"] == pytest.approx(0.06)
    assert first.loc["top:2", "value"] == pytest.approx(0.07)
    marginal = sr.marginal_alpha_profile(panel(), **options())
    rows = marginal.profile.set_index("group")
    assert rows.loc["top_minus_next:2", "mean"] == pytest.approx(0.04)
    assert rows.loc["top_minus_2k:2", "mean"] == pytest.approx(0.02)
    assert rows.loc["top_minus_next:2", "ci_low"] == pytest.approx(0.04)


@pytest.mark.parametrize(
    "returns,want", [((0.01, 0.01, 0.01, 0.01), 0), ((0, 0.02, 0.04, 0.06), -0.04)]
)
def test_saturation_and_reversal_are_not_relabelled(returns, want):
    result = sr.marginal_alpha_profile(panel(returns), **options())
    assert result.profile.set_index("group").loc["top_minus_next:2", "mean"] == pytest.approx(want)


def test_missing_labels_do_not_backfill_and_incomplete_k_is_explicit():
    data = panel()
    data.loc[data.symbol == "0", "ret"] = np.nan
    result = sr.tail_return_profile(data, **options())
    top = result.by_date[result.by_date.group == "top:2"]
    assert top.value.isna().all()
    assert set(top.status) == {"missing_labels"}
    assert set(top.n_labels) == {1}
    opts = options() | {"ks": (3,)}
    result = sr.marginal_alpha_profile(panel(), **opts)
    assert result.by_date.value.isna().all()
    assert set(result.by_date.status) == {"insufficient_scores"}


def test_tie_order_and_fingerprint_do_not_depend_on_input_row_order():
    data = panel()
    data["score"] = 1.0
    a = sr.tail_return_profile(data, **options())
    b = sr.tail_return_profile(data.sample(frac=1, random_state=5), **options())
    pd.testing.assert_frame_equal(a.by_date, b.by_date)
    assert a.summary["input_fingerprint"] == b.summary["input_fingerprint"]
    assert a.summary["tied_score_rows"] == len(data)
    assert a.by_date.query("group == 'top:1'").value.iloc[0] == 0.08


def test_dates_with_no_valid_scores_remain_in_block_grid():
    data = panel()
    data.loc[data.date == data.date.unique()[3], "score"] = np.nan
    result = sr.tail_return_profile(data, **options())
    row = result.profile.set_index("group").loc["top:1"]
    assert row.n_dates == 8
    assert row.n_eligible_dates == 7
    assert result.by_date.query("group == 'top:1'").shape[0] == 8
    pd.testing.assert_frame_equal(result.profile, sr.tail_return_profile(data, **options()).profile)


def test_too_few_dates_never_produces_zero_interval():
    result = sr.tail_return_profile(panel(dates=2), **options())
    assert result.profile.ci_low.isna().all()
    assert set(result.profile.interval_status) == {"insufficient_dates"}


@pytest.mark.parametrize("mutation", ["duplicate", "null_symbol", "invalid_date", "roles"])
def test_invalid_identities_are_rejected(mutation):
    data = panel()
    opts = options()
    if mutation == "duplicate":
        data = pd.concat([data, data.iloc[:1]])
    elif mutation == "null_symbol":
        data.loc[0, "symbol"] = None
    elif mutation == "invalid_date":
        data["date"] = "invalid"
    else:
        opts["score_col"] = "ret"
    with pytest.raises(ValueError):
        sr.tail_return_profile(data, **opts)


@pytest.mark.parametrize("ks", [(0,), (1, 1), (2, 1), (1.5,), (True,)])
def test_invalid_k_is_not_coerced(ks):
    with pytest.raises(ValueError):
        sr.tail_return_profile(panel(), **(options() | {"ks": ks}))


def test_block_cannot_exceed_full_date_grid():
    with pytest.raises(ValueError, match="block"):
        sr.tail_return_profile(panel(dates=1), **options())


def test_numeric_dates_are_rejected_instead_of_merging_cross_sections():
    data = pd.DataFrame(
        {"date": [20200101, 20200102], "symbol": ["a", "b"], "score": [2.0, 1.0], "ret": [0.1, 0.2]}
    )
    with pytest.raises(ValueError, match="date"):
        sr.tail_return_profile(data, **(options() | {"statistics": sr.BlockStatistics(1, 10, 2)}))
