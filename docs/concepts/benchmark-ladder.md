# 市场基准比较

[English canonical page](benchmark-ladder.en-US.md)

本页说明回测内 benchmark 和事后收益比较的接口。组合运行与配置入口见[配置说明](../orchestration/reference/configuration.md)。

## 回测内 benchmark

`backtest.benchmark_symbol` 和 `backtest.benchmark_returns_file` 二选一。收益数据可用时，运行结果会在 `summary.json` 中记录 `backtest.benchmark`、`backtest.active`，并生成 `backtest_benchmark.csv` 和 `backtest_active.csv`。

如需在同一次回测中增加其他对照，可配置 `backtest.benchmark_compare`。每条配置需在 `symbol` 和 `returns_file` 中二选一。系统会生成 `backtest_benchmark_compare_summary.csv`，并为每条对照生成 `backtest_benchmark_compare_<name>.csv`。这些对照不会改变主 benchmark。

## 事后 benchmark 比较

`portfolio_backtester.benchmark_ladder` 模块用于比较已有的策略收益和 benchmark 收益文件，Python 入口为 `build_benchmark_ladder(config, config_dir=...)`。当前没有注册 `strategy backtest benchmark-ladder` 命令。

配置需提供 `strategy_returns_file`，可选 `strategy_return_col`、`expected_market` 和 `periods_per_year`，并通过 `primary_benchmark` 或 `comparisons` 提供 benchmark。相对路径以 `config_dir` 为基准。

日期列支持 `trade_date`、`date`、`period_end` 或 `index`。未指定收益列时，模块依次查找 `strategy_return`、`benchmark_return`、`net_return`、`return` 和 `active_return`。日频收益需配置含 `entry_date` 与 `exit_date` 的 `periods_file`，区间复利默认不计入场日。

结果行包含对齐周期数、策略与 benchmark 总收益、主动收益统计、市场标签和状态。市场不匹配或没有重叠日期时状态为 `incompatible`。文件缺失或收益数据不可用时为 `unavailable`。`attribution_available` 只表示归因文件是否存在，模块不会计算归因。

`periods_per_year` 默认为 `12`，应按收益频率设置以便解释年化统计。本仓库提供比较机制，不替研究者选择 benchmark，也不判断策略是否可投资。
