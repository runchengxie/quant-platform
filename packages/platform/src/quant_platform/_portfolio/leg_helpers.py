from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from typing import cast as cast

import pandas as pd
from quant_backtest_core.daily._period_helpers import (
    _compute_trade_summary as _compute_trade_summary,
)
from quant_backtest_core.daily._period_helpers import (
    _drift_previous_weights as _drift_previous_weights,
)
from quant_backtest_core.daily.leg_financial import (
    _build_backtest_leg_result as _build_backtest_leg_result,
)
from quant_backtest_core.daily.leg_financial import (
    _build_leg_turnover_report as _build_leg_turnover_report,
)
from quant_backtest_core.daily.leg_financial import _next_position_state as _next_position_state

from .execution import CostModel as CostModel
from .execution import SlippageModel as SlippageModel
from .portfolio_weights import (
    build_position_weights,
    clean_position_weights,
    limit_weight_turnover,
)
from .pricing import slippage_pricing_row as slippage_pricing_row
from .selection_controls import TargetWeightPolicy
from .turnover import (
    RebalanceTurnoverReport as RebalanceTurnoverReport,
)
from .turnover import (
    build_rebalance_turnover_report as build_rebalance_turnover_report,
)
from .turnover import (
    turnover_from_trade_weights as turnover_from_trade_weights,
)
from .types import BacktestLegResult as BacktestLegResult
from .types import BacktestPositionState


@dataclass(frozen=True)
class _TargetWeightsAndExit:
    target_weights: pd.Series
    requested_weights: pd.Series


def _build_target_weights_and_exit(
    *,
    day: pd.DataFrame,
    holdings: list[str],
    pred_col: str,
    side: Literal["long", "short"],
    weighting_mode: str,
    weighting_liquidity_col: str,
    previous: BacktestPositionState,
    max_turnover_per_rebalance: float | None,
    selection_min_score: float | None,
    target_weight_policy: TargetWeightPolicy,
    target_slot_count: int,
    preserve_gross_exposure: bool,
) -> _TargetWeightsAndExit:
    if not holdings:
        empty = pd.Series(dtype=float)
        return _TargetWeightsAndExit(empty, empty)
    target_weights = build_position_weights(
        day,
        holdings,
        pred_col,
        side=side,
        weighting=weighting_mode,
        liquidity_col=weighting_liquidity_col,
        target_weight_policy=target_weight_policy,
        target_slot_count=target_slot_count,
    )
    requested_weights = limit_weight_turnover(
        previous.weights,
        target_weights,
        max_turnover_per_rebalance,
        preserve_gross_exposure=preserve_gross_exposure,
    )
    if selection_min_score is not None and not preserve_gross_exposure:
        requested_weights = clean_position_weights(
            requested_weights.reindex(holdings).dropna(),
            preserve_gross_exposure=False,
        )
    return _TargetWeightsAndExit(
        target_weights=target_weights,
        requested_weights=requested_weights,
    )
