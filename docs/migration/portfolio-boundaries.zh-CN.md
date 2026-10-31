# 组合模块归属与兼容迁移

语言：简体中文 · [English](portfolio-boundaries.md)

历史目录 `packages/portfolio-backtester` 已退役，平台源码迁入
`packages/platform/src`。这次调整明确代码归属和依赖关系，不表示 Rust
已经完整复现所有历史 Python 回测。

## 公开入口

| 导入路径 | 职责 |
| --- | --- |
| `quant_backtest_engine.EngineClient` | 独立的标准库 SDK，负责二进制摘要固定、进程调用和数量规划及逐日协议校验，返回字典 |
| `quant_platform.backtest.engine_sessions.EngineClient` | 组合 SDK 调用，仅转换平台 pandas 分析结果 |
| `quant_platform.backtest.contracts` | 标准结果类型、后端协议和注册表 |
| `quant_platform.backtest.ledger` | 不依赖模拟器的账本数据结构和勾稽 |
| `quant_platform.portfolio` | 组合构造、分配和优化 |
| `quant_platform.analytics` | 指标、归因、风险和报表 |
| `quant_platform.backtest.legacy` | 显式保留的 Python 兼容后端和模拟流程 |

公开入口的子模块沿用熟悉的模块名，例如 `quant_platform.analytics.metrics`、
`quant_platform.portfolio.optimization` 和 `quant_platform.backtest.legacy.execution_sim`。
旧命名空间暂时作为明确的兼容别名保留。函数和类共用一份实现，普通模块别名保留对象身份，
使已有测试补丁继续有效。包代理保留自身搜索路径，让旧子模块解析到对应别名。
不引入全局导入钩子，不复制算法，也不修改已保存数据的 schema 标识符。

原有内部实现暂时整体放在 `quant_platform._portfolio`，它不是公开 API。
公开入口按需加载。导入通用契约或数值指标时，不应加载旧执行模拟器。
先保留内部依赖图，有助于避免同时重写大量相对导入和金融算法。

## 调用方怎么改

在 platform 检出目录运行 `uv sync --locked --extra engine`，安装可选的引擎 SDK
适配器。只使用基础分析功能无需安装 SDK 或 Rust 可执行文件。开发依赖组包含固定
版本的 SDK，确保适配器回归测试仍然执行。

```python
from quant_platform.analytics.metrics import summarize_ic
from quant_platform.backtest.contracts import CanonicalBacktestResult

# 明确标识仍在使用的 Python 兼容流程
from quant_platform.backtest.legacy.execution_sim import ExecutionSimConfig

# 独立字典接口，无需安装 platform
from quant_backtest_engine import EngineClient as WireEngineClient
```

深层导入可查[模块映射表](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/portfolio-module-map.json)。
平台编排已使用这些公开归属。`scripts/dev/check_legacy_imports.py` 阻止第一方生产代码
重新直接导入旧命名空间。外部调用方迁移期间仍可使用旧导入，兼容测试也会继续验证它们。
通用契约和 wheel 导入检查独立于旧包执行。

## 为什么还有 Python 实现

公司行动、应收款、退市政策、日成交量容量、分期费率和完整历史执行证据流程，
在具体调用方获得经过验证的替代路径前，继续使用已有 Python 实现。
配置的 T+1、报价权限和逐日余额，不足以证明上述机制已经等价。
Rust 适配器继续标注 `execution_aware=False`，不会补造完整统一账本。
数量规划里的卖出收入仍是估算，以实际执行为准。

runtime 通过显式 `legacy` 可选依赖安装旧后端。只运行 Rust 任务无需安装 platform。
旧任务协议、请求摘要和结果读取保持兼容。缺少可选依赖时明确失败，
不会静默切换到另一套金融假设。

## 最终删除条件

历史目录的移动已完成，兼容命名空间尚未删除。退役某项 Python 计算或旧导入前，需要：

1. 清点实际调用方，包括生产发布路径、定时任务和外部用户。
2. 明确时钟、结算、费用、公司行动和结果要求。
3. 对照合成案例、现金、股份、成交及代表性工作流，解释差异，并在需要时验证完整证据映射。
4. 先合并提供方，再更新调用方版本，记录联合测试的提交组合。
5. 验证干净 wheel 安装、历史结果读取及历史版本复现。
6. 兼容义务结束后，通过有版本记录的发布移除旧导入。不能连同无关分析功能一起删除。

这次源码迁移不切换运行任务、生产发布、数据或定时路径。
仓库导入扫描不能证明外部和已部署调用方都已消失，后者仍是独立的退役条件。
