# 因子归因实现计划

> 给智能体开发者：必须使用 `superpowers:subagent-driven-development` 或 `superpowers:executing-plans`，按任务逐项执行。步骤使用复选框跟踪。

目标：增加主动收益和主动风险分解，未来接入平台风险模型并发布归因证据。

设计说明：`docs/superpowers/specs/2026-09-02-factor-attribution-design.md`

- [x] 为收益核对、风险核对以及资产和因子不匹配增加测试。
- [ ] 运行专项测试，并确认实现前测试按预期失败。
- [x] 实现因子收益贡献、特质残差、成本拖累、因子方差贡献和特质方差贡献。
- [x] 记录 Brinson 归因仍属于独立语义层的原因。
- [ ] 运行 `uv run --extra dev pytest tests/test_factor_attribution.py -q`。
- [ ] 运行仓库 lint、格式、类型、完整测试和可维护性检查。
