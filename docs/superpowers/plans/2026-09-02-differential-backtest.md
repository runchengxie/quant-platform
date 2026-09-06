# 差异化回测实现计划

> 给智能体开发者：必须使用 `superpowers:subagent-driven-development` 或 `superpowers:executing-plans`，按任务逐项执行。步骤使用复选框跟踪。

目标：比较两个标准后端结果，生成局部化且机器可读的差异，供未来形成 RQAlpha 差异证据。

设计说明：`docs/superpowers/specs/2026-09-02-differential-backtest-design.md`

- [x] 为持仓、净值定位、相同结果和能力差异增加专项测试。
- [ ] 运行专项测试，并确认实现前测试按预期失败。
- [x] 实现 `DifferentialBacktestReport` 和 `compare_backtest_results()`。
- [x] 记录 RQAlpha 和未来适配器的职责，以及当前订单和成交匹配的限制。
- [ ] 运行 `uv run --extra dev pytest tests/test_differential_backtest.py -q`。
- [ ] 运行仓库 lint、格式、类型、完整测试和可维护性检查。
