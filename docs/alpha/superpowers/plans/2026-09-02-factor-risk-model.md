# 因子风险模型实现计划

> 给智能体开发者：必须使用 `superpowers:subagent-driven-development` 或 `superpowers:executing-plans`，按任务逐项执行。步骤使用复选框跟踪。

目标：增加符合 PIT 要求的因子协方差和特质风险估计，并输出平台原生的 pandas 结果。

架构：明确保留因子构造过程。风险模型原语接收预先计算的暴露、因子收益和特质收益，拒绝未来观测，并在不导入组合代码的前提下计算 `X F X' + D`。

技术栈：Python 3.12、pandas、NumPy、pytest。

设计说明：`docs/superpowers/specs/2026-09-02-factor-risk-model-design.md`

## 全局约束

- 不得导入 `portfolio_backtester` 或 `strategy-pipeline`。
- 所有历史行的日期必须不晚于 `as_of`。
- 不新增专有供应商对象或数据获取器。
- 风险模型证据与优化器证据分开保存。

### 任务 1：定义风险模型测试

涉及文件：

- 新建：`tests/test_risk_model.py`

- [x] 增加投影协方差、正特质风险、未来数据拒绝、因子不匹配和协方差收缩测试。
- [ ] 运行 `scripts/dev/run_tests.sh` 或 `uv run --extra dev pytest tests/test_risk_model.py -q`，确认实现前测试按预期失败。

### 任务 2：实现并导出风险模型

涉及文件：

- 新建：`src/alpha_research/risk_model.py`
- 修改：`src/alpha_research/__init__.py`
- 修改：`tests/test_package_smoke.py`

- [x] 实现 `FactorRiskModelEstimate` 和 `build_factor_risk_model()`。
- [x] 强制检查有限值、精确的因子和资产身份、明确的 `as_of`、最小观测数量和可选对角收缩。
- [x] 导出 API，并在包冒烟测试中登记自有模块。
- [ ] 运行 `uv run --extra dev pytest tests/test_risk_model.py tests/test_package_smoke.py -q`。

### 任务 3：记录并验证

涉及文件：

- 新建：`docs/concepts/factor-risk-model.md`

- [x] 记录归属、模型公式、PIT 行为和未来集成方式。
- [ ] 使用 `scripts/dev/run_tests.sh` 运行 lint、格式、类型、完整测试和可维护性检查。
