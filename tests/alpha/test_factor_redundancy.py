import numpy as np
import pandas as pd
import pytest


def panel():
    index = pd.MultiIndex.from_product(
        [pd.to_datetime(["2020-01-01"]), list("abcd")], names=["date", "symbol"]
    )
    return pd.DataFrame(
        {"a": [1.0, 2.0, 3.0, 4.0], "b": [1.0, 2.0, 3.0, 4.0], "c": [4.0, 3.0, 2.0, 1.0]},
        index=index,
    )


def run(frame=None, **kwargs):
    from alpha_research.factor_redundancy import factor_redundancy

    return factor_redundancy(
        panel() if frame is None else frame, top_fraction=0.25, min_cross_section=3, **kwargs
    )


def test_duplicate_and_reverse_signal_are_distinct_in_tails_but_same_rank_direction():
    result = run()
    pairs = result["pairs"].set_index(["left", "right"])
    assert pairs.loc[("a", "b"), "spearman"] == pytest.approx(1)
    assert pairs.loc[("a", "b"), "top_jaccard"] == 1
    assert pairs.loc[("a", "c"), "spearman"] == pytest.approx(-1)
    assert pairs.loc[("a", "c"), "top_jaccard"] == 0
    assert pairs.loc[("a", "c"), "top_bottom_jaccard"] == 1
    assert result["rank"].iloc[0].participation_ratio == pytest.approx(1)


def test_ties_are_retained_with_actual_tail_sizes():
    frame = panel()
    frame["a"] = [1.0, 4.0, 4.0, 4.0]
    row = run(frame)["pairs"].iloc[0]
    assert row.top_size_left == 3
    assert row.top_size_right == 1
    assert row.top_jaccard == pytest.approx(1 / 3)


def test_constant_and_incomplete_common_samples_do_not_create_effective_rank():
    frame = panel()
    frame["b"] = 1.0
    assert run(frame)["rank"].iloc[0].status == "constant_signal"
    frame = panel()
    frame.loc[frame.index[:2], "b"] = np.nan
    result = run(frame)
    assert result["rank"].iloc[0].status == "insufficient_common_sample"
    assert pd.isna(result["rank"].iloc[0].participation_ratio)
    assert result["coverage"].set_index("factor").loc["b", "coverage"] == 0.5


def test_future_dates_do_not_change_past_statistics():
    original = run()
    future = panel()
    future.index = pd.MultiIndex.from_product(
        [pd.to_datetime(["2021-01-01"]), list("abcd")], names=["date", "symbol"]
    )
    future *= 1e9
    combined = run(pd.concat([panel(), future]))
    for key in original:
        pd.testing.assert_frame_equal(
            original[key],
            combined[key]
            .loc[combined[key].date.eq(pd.Timestamp("2020-01-01"))]
            .reset_index(drop=True),
        )


@pytest.mark.parametrize(
    "case", ["duplicate", "infinite", "index", "fraction", "boolean", "columns"]
)
def test_malformed_inputs_fail(case):
    from alpha_research.factor_redundancy import factor_redundancy

    frame, fraction, minimum = panel(), 0.25, 3
    if case == "duplicate":
        frame = pd.concat([frame, frame])
    elif case == "infinite":
        frame.iloc[0, 0] = np.inf
    elif case == "index":
        frame = frame.reset_index()
    elif case == "fraction":
        fraction = 0.6
    elif case == "boolean":
        minimum = True
    else:
        frame.columns = ["a", "a", "c"]
    with pytest.raises(ValueError):
        factor_redundancy(frame, top_fraction=fraction, min_cross_section=minimum)
