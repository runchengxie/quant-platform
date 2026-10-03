# Sequenced execution

Language: English · [简体中文](sequenced-execution.md)

`SequencedExecutionBackend` sends targets for multiple rebalance decisions through the shared daily execution simulator. It returns a `CanonicalBacktestResult` with orders, fills, and a daily ledger. Provide one `research.clock.v1` clock per `rebalance_date`; each `entry_date` must fall within that decision's execution window.

```python
from portfolio_backtester.backends import SequencedExecutionBackend, SequencedExecutionRequest
from portfolio_backtester.execution_sim import ExecutionSimConfig

result = SequencedExecutionBackend().run(
    SequencedExecutionRequest(
        positions=targets,  # rebalance_date, entry_date, symbol, weight
        pricing=daily_prices,  # trade_date, symbol, close, amount, tradable, ...
        decision_clocks=clocks,  # {rebalance_date: research.clock.v1}
        config=ExecutionSimConfig(enabled=True, liquidity_cols=("amount",)),
        tradable_col="tradable",
    )
)
```

The backend validates target dates and weights, clock coverage, execution windows, pricing dates, and configured market-rule inputs. If price-limit or listing-status checks are enabled, their daily input columns must be present, complete, and match the simulator configuration.

These checks do not prove that the data used to create each target was available at that decision time. Callers must retain source digests and establish input visibility separately; `PointInTimeDataView` can filter timestamped inputs. Without that evidence, treat the result as an execution diagnostic, not a point-in-time-compliant backtest.

`write_execution_aware_result_bundle` currently accepts a single decision clock and rejects a multi-decision result. Corporate actions for raw prices must be supplied as explicit `CorporateAction` events. If only adjusted prices are available, record the run as a price-proxy experiment.
