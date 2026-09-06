# 因子目录实现计划

> 给智能体开发者：必须使用 `superpowers:subagent-driven-development` 或 `superpowers:executing-plans`，按任务逐项执行。步骤使用复选框跟踪。

目标：增加稳定的因子版本身份和按日期记录的证据摘要，供工作区发布和 Dashboard 检查。

设计说明：`docs/superpowers/specs/2026-09-02-factor-catalog-design.md`

- [x] 为往返序列化、重复版本、无效依赖或哈希，以及非有限证据增加测试。
- [ ] 运行专项测试，并确认实现前测试按预期失败。
- [x] 实现 `FactorSpec`、`FactorEvidenceSummary` 和 `FactorCatalog`。
- [x] 记录 RQFactor 与 Alphalens 的关系及归属边界。
- [ ] 运行 `uv run --extra dev pytest tests/test_factor_catalog.py -q`。
- [ ] 运行仓库 lint、格式、类型、完整测试和可维护性检查。
