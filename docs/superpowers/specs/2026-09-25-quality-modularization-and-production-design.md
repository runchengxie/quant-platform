# 质量债务、模块边界与生产发布设计

## 目标

在保持现有 Python API 和研究结果不变的前提下，修复已盘点的类型与 Ruff 问题，拆分三个职责过重的模块，为 `research-contracts` 建立可信的直接测试和覆盖率，补齐组合约束诊断测试，并在所有代码变更合入且验证通过后，将最新 `quant-platform` 提交发布到 production。

## 范围

本设计覆盖以下五个可独立验证的工作包：

1. `research-contracts` 测试、实际包覆盖率和覆盖率门禁。
2. 组合约束可行性诊断现状核查和直接测试。
3. 执行模拟核心拆分。
4. 事件流训练模块拆分。
5. 编排输出摘要模块拆分。

静态检查范围包括 `pyproject.toml` 中 `ruff.extend-exclude` 列出的全部目录，以及 `ty` 当前配置纳入的全部源码和脚本。三个大模块及 contracts 是优先工作包，不代表其他被排除目录可以跳过。完成后应清除这些范围内可修复的 Ruff 和 `ty` 诊断，并让完整配置范围通过阻断型检查。确需保留的诊断必须有逐条、就近、说明原因的规则，不得用扩大的目录级忽略替代修复。

生产发布只包含 `quant-platform`。不修改其他框架版本、部署仓库配置、scheduler、凭据、研究数据或运行状态。

## 当前证据

核查基线为 `main` 提交 `adf3155bc1590ae63912f4db3503ce2633f32d46`。主检出干净且与 `origin/main` 同步。production 的 `current` 指向 `c49ed818521fc82c4ce49f806c0b97b4a373eefd`，比核查基线落后 3 个提交。

`research-contracts` 的代码从 `.venv/lib/python3.13/site-packages/research_contracts` 导入。用已有相关测试测量这个实际导入包，语句覆盖率为 24%，共 2,225 条语句。包内没有专门的测试目录。`quant-research` 和 `quant-intel-platform` 直接使用本包 API，契约正确性会影响多个消费者。

已识别的三个大模块及其调用边界如下：

| 当前文件 | 行数 | 主要职责 |
| --- | ---: | --- |
| `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/core.py` | 1,065 | 容量模拟、调整后 NAV、理想 NAV、执行表准备 |
| `packages/microstructure/src/ticknet/eventstream/train.py` | 972 | 配置、数据加载、评估、检查点、训练循环和 CLI |
| `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_sections.py` | 805 | 回测、评估、持仓、执行和诊断摘要构造 |

执行模拟包已有 `capacity.py`、`orders.py`、`corporate_actions.py`、`reporting.py`、`models.py` 和 `results.py` 等边界。`execution_sim.__init__` 从 `core.py` 导出入口，测试也直接导入该模块。事件流的其他模块直接从 `train.py` 导入 `EventstreamConfig` 和 `list_packed_days`。输出摘要测试直接导入 `output_summary_sections.py` 中的构造函数。拆分必须保留这些兼容入口。

执行模拟测试还会通过 `execution_sim.core._build_execution_tables` 做 monkeypatch。迁移时应把测试改为 patch 实际定义函数的模块，或提供明确的兼容接口，并验证替换后调用路径仍符合预期。不能只保留同名别名，却让调用改走另一份全局引用。

平台已有几处与隐式系统论文思路相通的边界：`ResearchClock` 检查信息截止、信号、决策和执行窗口的时间顺序，优化请求校验部分权重边界，QP 结果包含约束残差和失败时的等权回退，执行层区分目标、调仓计划、订单和成交。本设计借用的是先检查因果性、可行性和自由度，再优化的工程顺序，不把 descriptor-system 定理当成金融市场结论。

对目标模块和 contracts 运行定向 `ty --error-on-warning` 得到 15 条诊断，集中在事件流训练的 `DataLoader`、NumPy 数组类型和输出摘要日期转换。对目标目录运行同一 Ruff 规则集合得到 426 条诊断，其中超长行 285 条、Unicode 标点提示 96 条、导入顺序 28 条、复杂函数 6 条，其余为少量集合写法、分号和未使用导入问题。中文文案与注释中的全角标点需逐项判断，不能为通过扫描而改坏中文文本。

此前完整 `ty check --error-on-warning` 检查约有 414 条诊断，Ruff 被排除范围的定向盘点约有 463 条诊断，具体数量会随基线提交和规则版本变化。实施前须在最新 `main` 上重跑完整扫描，记录机器可复现的基线、命令和按目录分布。最终验收覆盖整个配置范围，不能只消除三个优先模块中的问题。

指定最新提交的 production 发布 dry-run 已成功，目标为 `/home/richard/code/production/quant-platform/releases/adf3155bc1590ae63912f4db3503ce2633f32d46`，并会原子切换 `current`。尚未执行生产切换。

## 设计

### 1. 为 contracts 建立直接测试

在 `tests/contracts/` 按领域组织测试，直接调用 `research-contracts` 当前公开导出，以及消费者直接使用的 `promotion_evidence_checks` 等子模块。测试输入使用临时目录、合成 JSON 和临时文件，不读取真实研究数据或凭据。

重点覆盖 artifact envelope 的序列化与无效输入、manifest 和 ownership 校验、文件收据与 SHA-256、发布清单、研究时钟的时区和因果约束、根运行清单、target lineage，以及 A 股 readiness 和 promotion evidence 检查。每个校验 API 至少有一个有效样例和一个拒绝非法输入的样例。文件系统 API 覆盖缺失文件、错误摘要和原子写入失败等边界。

`ResearchClock` 测试显式覆盖信息截止不晚于信号、信号不晚于决策、决策不晚于最早下单时间和执行窗口起点、执行窗口起点不晚于终点、终点不晚于估值时间，以及最早下单时间不晚于执行窗口终点等适用约束，并覆盖缺少可选执行窗口字段时的行为。共享 contract 只验证时间证据是否自洽，不推断策略信号是否有预测力。

根覆盖率入口显式加入 `--cov=research_contracts`，测量当前测试实际运行的安装包，并避免把未执行的源码目录误当作覆盖率。报告应能显示该包的真实导入路径。新增 contracts 行为测试合入后，以 80% 语句覆盖率作为初始门槛，并对公开导出的每个验证器保留正向与负向行为断言。若测试暴露未被消费者或文档引用的历史模块，先核实外部消费者后再决定保留、标记或删除，不以覆盖率名义改动其语义。

### 2. 拆分执行模拟核心

将 `core.py` 中的编排逻辑移入职责模块：

- 容量执行流程进入 `capacity_simulation.py`。
- 调整后 NAV 计划、订单保留、逐日执行和 ledger 进入 `adjusted_nav.py`。
- 理想日 NAV 目标、ledger 和逐日结果进入 `ideal_nav.py`。
- 执行表与可交易标的准备进入 `table_preparation.py`。

`core.py` 保留薄兼容层，继续导出当前公开函数和既有测试/内部消费者使用的符号。领域计算、撮合次序、费用、corporate action 和结果 schema 均不得变化。现有执行模拟回归测试作为迁移基线，增加模块级测试只验证边界调用，不复制原测试逻辑。

迁移和文档核查应沿用现有 `desired target -> rebalance plan -> order -> fill` 生命周期，清楚区分策略目标、约束后的执行计划和成交后的实际结果。现有 schema 没有依据时，不为追求命名统一改写历史输出。

### 3. 核查组合约束可行性与非唯一性诊断

`PortfolioOptimizationRequest` 已检查资产边界和简单的 long-only 权重上下界，QP backend 会检查结果约束残差，并在失败时尝试等权回退。为这些现有行为增加直接测试，覆盖可行边界、冲突暴露约束、回退可行与不可行的情况，并审查诊断是否能说明约束违反原因。

实施前对等式约束秩、自由度和近似非唯一解能力做一次窄范围 API 评估。若现有结果不足以让调用者判断可行性，新增诊断应保持策略无关，并兼容现有 `PortfolioOptimizationResult` 与 JSON schema。不要在本轮引入依赖特定优化器的近最优解搜索、通用稳定性报告或状态估计接口。任何需要改变公开 API 或 schema 的扩展，先形成单独设计和迁移方案。

### 4. 拆分事件流训练模块

把 `EventstreamConfig`、数据加载器、评估、检查点处理、训练循环和命令行入口拆到各自模块。配置类型放入独立训练配置模块，避免让现有 `eventstream/config.py` 同时承担包路径和训练配置两种职责。`train.py` 保留兼容导出，保证 benchmark、input profile、materialized 数据集和 gradient audit 的既有导入继续可用。

训练样本选择、日期排序、数据集兼容检查、检查点恢复、实验签名、随机种子及训练结果必须与拆分前一致。用现有 eventstream 测试保护 Python 行为，Rust 相关 CI 继续验证 Rust 包的 parity。

### 5. 拆分输出摘要构造

把日期、路径、标量和 DataFrame 记录格式化抽到共享 helper。按输入与模型信息、评估与回测结果、持仓与执行、诊断与晋级摘要拆分 builder 模块。`output_summary_sections.py` 保留 `build_run_summary_sections` 聚合入口，并继续导出目前被测试和消费者直接导入的函数。

输出 key、嵌套结构、缺失值表示、路径文本和日期格式必须保持逐字兼容。现有 pipeline output 和 output summary tests 应在迁移过程中作为固定行为基线。

### 6. 类型与 Ruff 门禁

每个工作包先记录其文件级诊断基线，修复实现和类型声明中的真实问题。拆分后立即运行该目录的 Ruff、`ty` 和行为测试。解决目录已有 Ruff 问题后，删除该目录对应的 `extend-exclude` 项，并保持仓库规则集一致。

全角中文标点若确实用于中文注释或用户可见文案，应采用 Ruff 的明确配置或最小范围规则说明处理，不得转换为不合语境的半角标点。`ty` 的 `Unknown` 只有在类型确实无法由现有库 stub 表达时才允许在最小边界收窄，禁止新增整目录 warning 覆盖。最终 Ruff 应覆盖此前排除的所有目录，`ty check --error-on-warning` 应覆盖当前配置的完整源码与脚本范围并通过。完整检查范围及有理由保留的逐项例外须写入维护文档，避免后续静默扩大排除项。

## 实施顺序与交付

建议按以下 PR 顺序执行，每个 PR 都从当时最新 `origin/main` 建立独立 worktree：

1. contracts 直接测试、覆盖率统计和覆盖率门槛。
2. 优化约束可行性诊断核查和测试，只有证据表明缺少必要信息时才增加最小兼容诊断。
3. execution simulation 拆分及对应 Ruff/ty 清理。
4. eventstream training 拆分及对应 Ruff/ty 清理。
5. output summary 拆分及对应 Ruff/ty 清理，清理剩余已审计目录的 Ruff/ty 债务。
6. 全仓回归、依赖审计和 release readiness 检查，合并后发布 production。

PR 必须保留完整公开 CI。除各自聚焦的测试外，还要运行全量 pytest、全仓 Ruff、格式检查、受影响范围的 `ty`、维护性预算和 `pip-audit`。模块拆分的 PR 不得把行为修改与文件搬迁混在一起。

所有代码 PR 合入后，确认 production 发布源仓库干净、目标 SHA 是 `main` 可达提交且公开 CI 通过。对 `quant-platform` 单独运行部署发布器 dry-run，再以精确 SHA 发布，保留当前版和两个可安全保留的旧版本。发布后核对 manifest 中的提交与 `current`，运行包导入和公开契约 smoke test。异常时按清单原子切回发布前记录的 release。该仓库是公共 Python 库，没有独立常驻服务或消息发送入口，发布验证不应触发研究任务、scheduler 或真实投递。

## 不在本设计范围内

- 把研究、数据、执行服务迁移到 Java、Rust 或其他语言。
- 改写交易算法、费用语义、研究模型或契约 schema。
- 更新 `quant-research`、`quant-intel-platform` 或 `quant-intel-deploy` 的依赖锁和 production 版本。
- 清理历史生产 release、凭据、状态、日志或本地数据。

## 验收条件

- `tests/contracts/` 能独立验证共享契约，根覆盖率报告按 `research_contracts` 模块来源统计，并通过已配置的契约覆盖率门槛。
- 三个目标模块均完成职责拆分，原导入路径保持兼容，既有测试和输出契约不变。
- `ResearchClock` 的因果顺序、优化约束边界与执行层目标到成交的状态区分都有直接回归测试。优化结果能报告已验证的约束残差；若新增诊断，公开字段和 schema 有兼容性测试。
- 已审计的 Ruff 排除目录不再因历史债务整体跳过，目标范围没有未解释的 Ruff 诊断。
- 完整配置范围的 Ruff 和阻断型 `ty` 检查通过，保留的例外有针对性理由并记录在维护文档中。
- 全量 pytest、Ruff、格式、类型、维护性指标、依赖审计及 GitHub Actions 必需检查通过。
- production `current` 和 manifest 指向最后一个已合入且验证通过的 `main` SHA，发布后 smoke test 通过，旧 release 保留为可回滚目标。
