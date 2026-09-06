# 优化器后端边界实现计划

> 给智能体开发者：必须使用 `superpowers:subagent-driven-development` 或 `superpowers:executing-plans`，按任务逐项执行。步骤使用复选框跟踪。

目标：增加由平台负责的优化器请求和结果边界，并提供原生等权和 HRP 基线。

架构：将优化与回测和执行后端分开。外部求解器适配器在 pandas 和平台原生类型之间转换，不通过公开 API 泄露第三方对象。

技术栈：Python 3.12、pandas、NumPy、现有 HRP 实现、pytest。

设计说明：`docs/superpowers/specs/2026-09-02-optimizer-backend-boundary-design.md`

## 全局约束

- 不增加新的运行时依赖。
- 复用现有 HRP 实现，不复制代码。
- 新的请求和结果类型保持与框架无关。
- 本 PR 的原生优化模式只支持只做多。

### 任务 1：定义测试和标准类型

涉及文件：

- 新建：`tests/test_optimizer_backends.py`
- 新建：`src/portfolio_backtester/optimization.py`

- [x] 为等权、HRP 边界、注册表行为、资产不匹配和不可行边界编写测试。
- [ ] 运行 `uv run --extra dev pytest tests/test_optimizer_backends.py -q`，确认实现前测试按预期失败。
- [x] 实现请求和结果验证、注册表、等权基线和 HRP 适配器。
- [ ] 运行专项测试并确认通过。

### 任务 2：发布平台 API

涉及文件：

- 修改：`src/portfolio_backtester/__init__.py`
- 修改：`tests/test_package_smoke.py`
- 新建：`docs/concepts/portfolio-optimization-backends.md`

- [x] 导出优化器类型和原生后端。
- [x] 在包冒烟测试中登记新模块和导出项。
- [x] 记录外部适配器的采用顺序。
- [ ] 运行 `uv run --extra dev pytest tests/test_optimizer_backends.py tests/test_package_smoke.py -q`。

### 任务 3：仓库门禁

- [ ] 运行 `scripts/dev/run_tests.sh lint`。
- [ ] 运行 `scripts/dev/run_tests.sh format`。
- [ ] 运行 `scripts/dev/run_tests.sh typecheck`。
- [ ] 运行 `scripts/dev/run_tests.sh all`。
- [ ] 运行 `scripts/dev/run_tests.sh maintainability`，并将已有的门槛失败与本次改动分开记录。
