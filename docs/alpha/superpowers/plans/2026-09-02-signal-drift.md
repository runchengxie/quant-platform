# 信号漂移实现计划

> 给智能体开发者：必须使用 `superpowers:subagent-driven-development` 或 `superpowers:executing-plans`，按任务逐项执行。步骤使用复选框跟踪。

目标：生成由平台负责的信号群体漂移诊断，后续可发布为 Dashboard 研究证据。

设计说明：`docs/superpowers/specs/2026-09-02-signal-drift-design.md`

- [x] 为相同、偏移、过滤非有限值和参考群体为常数的群体增加测试。
- [ ] 运行专项测试，并确认实现前测试按预期失败。
- [x] 使用 PSI、KS、均值变化和标准差比值实现 `SignalDriftReport` 与 `summarize_signal_drift()`。
- [x] 记录漂移指标与生命周期决定之间的边界。
- [ ] 运行 `uv run --extra dev pytest tests/test_signal_drift.py -q`。
- [ ] 运行仓库 lint、格式、类型、完整测试和可维护性检查。
