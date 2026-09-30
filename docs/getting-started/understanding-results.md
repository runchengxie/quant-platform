# Understand backtest results

Language: English · [简体中文](understanding-results.zh-CN.md)

The default `run_backtest` result is a five-element tuple:

```python
stats, net_returns, gross_returns, turnover, periods = result
```

## Summary statistics

`stats` commonly includes total return, annualized return, annualized volatility, Sharpe ratio, maximum drawdown, and average turnover. Use the current implementation and tests as the authority for exact fields. A common access pattern is:

```python
summary = {
    "total_return": stats["total_return"],
    "annualized_return": stats["ann_return"],
    "annualized_volatility": stats["ann_vol"],
    "sharpe": stats["sharpe"],
    "max_drawdown": stats["max_drawdown"],
}
```

A metric may be `None` or `NaN` when there is not enough data to calculate it. Check the sample length and metric definition before comparing experiments.

## Net and gross returns

- `gross_returns` reflects returns along the portfolio path before modeled costs.
- `net_returns` uses the same path after modeled transaction costs and slippage.
- Their difference helps show whether turnover and execution assumptions materially reduce returns.

For example:

```python
cost_drag = gross_returns - net_returns
```

This cost drag is a model result, not an estimate of actual fills. Actual execution requires evidence such as orders, fills, and account ledgers.

## Holding-period details

`periods` is a list of dictionaries organized by holding period. Common fields include:

| Field | Meaning |
| --- | --- |
| `entry_date` | Start date of the holding period |
| `exit_date` | End date of the holding period |
| `net_return` | Net return for the holding period |
| `gross_return` | Gross return for the holding period |
| `turnover` | Turnover for the holding period |
| `positions` | Target positions used for the holding period |

Backends and configurations may add fields. For the full output contract, see [backtest outputs](../reference/outputs/backtest-outputs.md) and [position outputs](../reference/outputs/positions.md).

## Ask three questions before interpreting results

1. Did the return come from the portfolio path, or from omitted costs and pricing assumptions?
2. Were the signal, price, and tradability inputs available at the time represented by the backtest?
3. Is this a diagnostic result, or is it supported by complete execution evidence?

Backtest metrics alone cannot answer these questions. Review the input data, configuration, position artifacts, and execution evidence together.
