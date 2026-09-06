import numpy as np
import pandas as pd

from strategy_pipeline.pipeline.eval import _empty_period_result


def test_empty_period_result_preserves_public_result_shape() -> None:
    result = _empty_period_result()

    assert result["ic_series"].empty
    assert result["quantile_ts"].empty
    assert result["bt_net_series"].name == "net_return"
    assert result["bt_gross_series"].name == "gross_return"
    assert result["positions_by_rebalance"] is None
    assert result["eval_rebalance_dates"] == []
    assert result["backtest_rebalance_dates"] == []
    assert np.issubdtype(result["ic_series"].dtype, np.number)
    assert isinstance(result["bt_net_series"], pd.Series)
