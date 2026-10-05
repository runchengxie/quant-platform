# 防过拟合机制总览

语言：简体中文 · [English canonical](overfitting-controls.en-US.md)

> status: active
> owner: quant-market-research
> audience: human and agent
> last_verified: 2026-10-05
> source_of_truth: yes
> superseded_by: n/a

本页概述减少数据泄漏、验证不稳、特征选择偏差和重复试验偏差的方法。列出的机制不代表每次训练都会自动运行。详见[研究产物](../reference/research-outputs.en-US.md)、[编排配置](../../orchestration/reference/configuration.md)和[CLI 辅助工具](../../orchestration/reference/cli-helpers.md)。

## 主要风险与检查

| 风险 | 建议检查 |
| --- | --- |
| 历史数据包含当时不可见的信息 | PIT 股票池和版本化资产检查 |
| 训练和测试标签窗口重叠 | 时间切分、事件窗口清理和 CPCV |
| 相邻观测受相同市场环境影响 | 前推验证和滚动训练窗口 |
| 试验很多，只保留表现最好的结果 | 完整试验台账、DSR 和 PBO |
| 结果依赖某段特定行情 | CPCV 路径和场景重采样 |
| 相关特征互相掩盖贡献 | 消融、置换重要度、SFI 和 drop-column |

PIT 指按决策时点只使用当时可见的信息。CPCV 是组合式带清理交叉验证。DSR 会调整多次试验后挑选赢家产生的 Sharpe 偏差。PBO 估计样本内赢家在样本外排名变差的概率，CSCV 是常用计算方法之一。

## 仓库已有机制

| 机制 | 实现与边界 |
| --- | --- |
| 时间切分与事件窗口清理 | alpha 研究切分 API 接受 `cv_purge_mode` 的 `gap` 和 `event_window`。这不是单独注册的 `strategy alpha` CLI 命令。 |
| 前推验证和最终留出 | 流程支持 `eval.walk_forward` 和 `eval.final_oos`。候选确定前不要查看最终留出结果。 |
| CPCV 和 PBO | alpha 包含相关研究 API，但其 parser helper 没有注册为公开的 `strategy-pipeline` 命令。 |
| 特征证据 | alpha 包支持消融、置换重要度、因子 IC、SFI、相关性审计和 drop-column 模式。这些 parser helper 不是公开 CLI 子命令。 |
| 诊断 | `overfitting_diagnostics` 提供唯一性、负控制、场景回测和候选冻结模式，不会在普通训练中自动执行。 |
| 试验台账 | `ExperimentRegistry` 是追加式 JSON API，用于记录试验身份和状态，也不会扫描运行目录发现试验。 |
| 晋升门 | `alpha_research.promotion_gate` 根据给定报告和配置进行评估。运行前通过 `strategy-pipeline --help` 核对公开命令。 |

当前公开 CLI 没有注册旧文档中的命令，包括 `strategy alpha cpcv`、`strategy alpha pbo`、`strategy alpha feature-evidence`、`strategy trial-registry` 和 `strategy promotion-gate`。请使用包 API 或项目明确配置的研究 runner，并先核对其入口。

## 实际复核顺序

1. 固定数据资产、PIT 股票池、目标、特征、成本和组合构造，确保候选与基线口径一致。
2. 按时间验证。标签窗口可能重叠时，将 `cv_purge_mode` 设为 `event_window`，并确认所用 runner 确实把该设置传入切分 API。
3. 候选及规则确定前，不查看最终样本外留出结果。
4. 对比简单基线和候选，检查特征族消融、稳定性、相关性及特征重要度诊断。
5. 成功和失败的试验都要记录。DSR 和 PBO 依赖完整且可比的试验集合。
6. 将 CPCV 或场景重采样作为针对性压力检查，不能替代前推验证和最终留出。
7. 冻结候选及其证据后，再进行模拟或影子运行。

晋升门 API 可接收主评估、回测、前推、最终样本外、成本与换手报告，并可配置 CPCV 路径数、DSR 试验数等阈值。输入不完整或不可比时，阈值本身不能保证结论可靠。评估时同时检查数据和试验覆盖、IC、多空收益、Sharpe、回撤、换手、成本及暴露。单个高 Sharpe、特征重要度或模型运行都不足以支持晋升。
