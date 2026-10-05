# Alpha 研究产物

[English canonical](research-outputs.en-US.md)

本页说明本仓库 alpha 研究模块生成的报告和数据文件。它是产物参考，不代表每个模块都已注册为命令行子命令。当前公开 CLI 是 `strategy-pipeline`。运行 `strategy-pipeline --help` 可查看实际命令。旧文档中的 `strategy alpha ...` 命令并未注册到当前 CLI。

运行编排和 `summary.json` 顶层结构见[运行摘要章节](../../orchestration/output-summary.md)。跨项目产物约定见[公开 API 参考](../../reference/public-api.md)。

## 默认输出根目录

使用 alpha 共享路径解析器且未显式指定输出路径时，依次读取：

1. `ALPHA_RESEARCH_OUTPUT_ROOT`
2. `QUANT_PLATFORM_OUTPUT_ROOT`
3. `DATA_PLATFORM_ROOT/quant-platform/research`
4. `$XDG_STATE_HOME/quant-platform/research`。未设置时使用 `~/.local/state/quant-platform/research`

显式绝对路径按原路径使用，显式相对路径相对于当前工作目录。部分工具会相对于配置文件所在目录解析输出，使用前应核对对应模块说明。

## CPCV 报告

`alpha_research.cpcv` 和 `alpha_research.artifact_cpcv` 可将报告写到输出目录。共享默认目录为 `reports/cpcv_<tag>/`。未提供配置时 tag 为 `default`，显式输出目录优先。

报告包括：

- `cpcv_splits.csv`：切分定义、日期范围、purge／embargo 信息和状态。
- `cpcv_path_returns.csv`：重建路径的收益。
- `cpcv_path_metrics.csv`：路径样本数、Sharpe、收益、波动、回撤、IC、long-short、换手、成本拖累及可用的基准相对指标。
- `cpcv_summary.json`：切分和路径数量、最终 OOS 处理方式、purge 模式及路径汇总指标。

具体字段会因使用 pipeline 准备的上下文还是基于 artifact 的 CPCV 配置而异，应以相应运行模式的 summary 和测试为准。CPCV 是验证证据，不会自动批准候选策略。

## CSCV、PBO 和 DSR

`alpha_research.pbo` 模块读取带日期的收益矩阵，默认在 `reports/pbo/` 下写出 `pbo_splits.csv` 和 `pbo_summary.json`。可以传入可选的 `ExperimentRegistry` JSON，提供 DSR 所用的试验总数。注册表不会通过扫描运行目录自动生成。

summary 记录分组与切分数、候选与试验数、PBO、样本外 Sharpe 汇总、全样本选中的候选、最大回撤及 DSR 字段。候选收益列应使用共享日期索引，且彼此可比。

## 动态多信号组合

`alpha_research.dynamic_signal_ensemble` 模块优先使用配置中的 `output_dir`。相对路径相对于配置文件。未配置时使用共享默认目录 `reports/dynamic_signal_ensemble/`。产物包括：

```text
dynamic_scores.parquet
stock_weights.parquet
factor_weights.parquet
factor_monitor.csv
portfolio_monitor.csv
direction_calibration.csv
dynamic_signal_ensemble_summary.json
```

summary 包含 `schema_version`、`artifact_type`、`no_level2`、`rolling_metrics_shifted`、日期和信号数量、风险惩罚与相关性参数、活跃因子数量及换手均值、最终配置和文件路径。

Rank IC、ICIR、long-short、coverage 和 dispersion 的滚动诊断会在用于当期选择前滞后一周期。方向校准依据历史 Rank IC 和 inertia。反向证据不足时沿用上一期方向。该模块不读取 Level2、分钟线或执行系统的 `targets.json`。

## 特征证据

`alpha_research.feature_evidence` 辅助函数支持 `generate-ablation`、`summarize-ablation`、`permutation-importance`、`factor-ic`、`sfi`、`correlation-audit` 和 `drop-column-importance`。它们读取 YAML 配置，可输出 CSV 和／或 JSON。输出列会因模式不同而变化。

`generate-ablation` 生成配置和 `jobs.csv` 任务计划，不会执行这些任务。其他模式用于汇总已完成的证据或计算对应诊断。研究流程见[特征研究协议](../concepts/feature-research-protocol.md)。当前 `strategy-pipeline` CLI 没有把这些辅助函数注册为 `strategy alpha feature-evidence`。

## 防过拟合诊断

`alpha_research.overfitting_diagnostics` 模块提供事件唯一性、负控制、情景回测和候选冻结清单辅助函数，产物依模式而异：

- 唯一性：事件明细和 summary JSON。
- 负控制：CSV 报告。
- 情景回测：`scenario_paths.csv` 和 `scenario_summary.json`。
- 候选冻结：JSON 清单。

当前 `strategy-pipeline` CLI 没有暴露 alpha 命令组。使用旧命令示例前，应先检查模块参数定义和测试。

## 试验台账

`alpha_research.experiment_registry.ExperimentRegistry` 是由调用方维护的追加式 JSON 试验记录。文件顶层包含 `schema_version`、`trial_count` 和 `trials`。每条记录保存候选、特征集、股票池、持有期、参数、状态和由内容生成的稳定 `trial_id`。PBO 可通过可选输入读取该文件。

注册表不会递归扫描 `summary.json` 或 `config.used.yml`，也不会自动找回失败试验。应在运行实验时记录完整的尝试集合。

## 信号产物

`signals.parquet` 和 `signals.meta.json` 是 alpha 向回测交付的标准信号文件。字段、校验和元数据见[信号产物契约](signal-artifacts.en-US.md)。
