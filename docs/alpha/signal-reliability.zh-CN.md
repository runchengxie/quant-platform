# 截面信号可靠性诊断

语言：简体中文 · [English](signal-reliability.md)

这组接口用于检验：最高分股票是否还有额外排序信息，以及控制指定暴露后，
因子是否仍有预测信息。输出是研究统计，不能替代真实成本和成交约束下的组合回测，
也不能解释为因子的因果贡献或自动选择最优持仓数量。

## 使用接口

从 `alpha_research.signal_reliability` 导入 `BlockStatistics`、
`tail_return_profile`、`marginal_alpha_profile` 和 `conditional_factor_profile`。

```python
from alpha_research.signal_reliability import (
    BlockStatistics, tail_return_profile, marginal_alpha_profile,
    conditional_factor_profile,
)

stats = BlockStatistics(block_length=5, repetitions=1000, min_dates=20, seed=7)
tail = tail_return_profile(
    panel, score_col="score", target_col="future_return", ks=(10, 20, 50), statistics=stats,
)
marginal = marginal_alpha_profile(
    panel, score_col="score", target_col="future_return", ks=(10, 20, 50), statistics=stats,
)
conditional = conditional_factor_profile(
    panel, factor_cols=("factor",), control_cols=("size", "value"),
    industry_col="industry", min_obs=30, target_col="future_return",
    ks=(10, 20, 50), statistics=stats,
)
```

输入每行对应一个日期和股票，默认键为 `trade_date`、`symbol`，可通过
`date_col`、`symbol_col` 修改。日期转换为 UTC 日历日期。本地交易日应提供无时区日期。
股票标识转为字符串，规范化后重复的键会报错。各列角色必须不同。
K 必须为严格递增的正整数，默认高分优先，`ascending=True` 改为低分优先。
目标必须是小数单位的已实现收益。通过 `provenance` 记录周期、基准和调整方式。
接口不会自动减去市场或行业收益。非有限数值按缺失处理，输入行序不影响排序和指纹。

返回对象有三个字段：`summary` 记录产物类型、版本 1、输入指纹、日期、定义、
统计设置、声明的来源和限制。`by_date` 保存逐日 `group`、`metric`、`value`、
`status` 和样本数。`profile` 按组和指标保存各日期等权的均值、有效日期数和区间。

## 尾部收益与边际收益

`band:start:end` 是不重叠排名区间，`top:K` 是累计前 K 名。
先按有限分数排序，同分按股票标识决定顺序，再检查收益标签。
缺失收益不会使后面的股票补位。股票数不足或标签不全时不计算收益。
逐日记录 `requested_count`、`actual_count`、`n_labels`、`n_scores`、`n_universe`，
状态为 `ok`、`missing_labels` 或 `insufficient_scores`。不可用数值为 NaN。
汇总中的 `tied_score_rows` 统计各日存在同分的全部行数。

`top_minus_next:K` 比较前 K 名与第 K+1 到 2K 名。`top_minus_2k:K`
比较前 K 名与前 2K 名，在完整等权分组中等于前一差值的一半。
两项均要求完整的 2K 个分数和标签，指标为 `return_spread`。
区间直接从逐日配对差值计算，不能通过两个独立区间是否重叠代替。
名称中的 alpha 不代表自动做过风险调整，更不代表因果收益。

## 条件因子评估

每个因子的组名为 `factor:name`，有四项指标：

- `raw_full_rank_ic`：所有有效因子和标签样本的 Spearman IC。
- `raw_rank_ic`：与条件评估采用同一完整样本的原始 IC。
- `partial_rank_ic`：因子、标签和数值控制变量先转秩，因子秩和标签秩分别对
  同一控制设计回归，计算两组残差的 Pearson 相关。行业采用删一类的哑变量，含截距。
- `conditional_coefficient`：原始收益对标准化因子、标准化数值控制变量及行业的
  OLS 系数，单位为每一个因子截面标准差的收益，标准差使用 `ddof=0`。

现有因子取残差再与原始收益求相关的历史接口保持不变。
新统计描述的是线性条件关系。偏秩相关也不是非线性条件独立检验。
两种统计都不能恢复所谓上帝视角的真实贡献。

报告 `n_obs`、`n_raw_obs`、`n_universe`，以及控制设计的 `design_rank`、
`design_columns`、`condition_number`。不会自动选择或删除控制变量。
行业缺失会排除该样本，不会虚构一个行业类别。
常数、设计不满秩、标准化后条件数超过 `1e10` 或因子残差标准差低于 `1e-8`
时返回 `unidentified`。秩设计和线性设计分别检查。
其他状态包括 `insufficient_observations`、`insufficient_degrees_of_freedom`、
无控制变量时的 `not_requested`。`min_obs` 至少为三，观测数还必须超过完整设计列数。

### 配对模型增量

提供 `baseline_col`、`augmented_col` 和 `paired_provenance` 可比较增量。
后者包含 `baseline`、`augmented` 两组身份和非空的 `feature_change`。
两组均需提供不同的 `run_id`，以及相同的 `label_id`、`universe_id`、`split_id`、
`prediction_availability="before_label_start"`。英文页给出了完整构造示例。
这些是调用方声明，不能代替泄漏审计。

先匹配两个有限预测值的共同样本，报告 `n_prediction_pairs` 和原始股票池大小。
IC 再排除标签缺失。Top K 先排序再检查标签，不补位。
`incremental` 组的 `rank_ic_delta` 和 `incremental:top:K` 组的
`top_return_delta` 均为加入因子的模型减基线模型。
预测分数不需要是收益，不会直接与收益相减。
没有配对预测时 `incremental_status=not_provided`。有则为 `provided_declared_oos`。
这里不推断成本后增量，仍需使用已有执行系统提供配对证据。

## 区间、来源与限制

按输入中完整的日期网格做非循环移动区块 Bootstrap，保留指标缺失的位置。
每次抽取足够多的整块并截断到原长度。整个面板中缺失的日期无法凭空推断。
块长以输入日期数计，不得超过日期网格，应根据标签重叠和序列依赖选择。
重复次数为正，`min_dates` 至少为二，种子非负，置信水平严格位于零和一之间。

重采样后再对有限值求均值。有效数少于 `min_dates` 的重采样无效。
有效重采样比例低于 90% 或不足两次时，区间状态为 `insufficient_resamples`。
原始有效日期不足时为 `insufficient_dates`，有均值仍会报告。
区间状态为 `ok` 才可使用。它们是逐项描述性百分位区间，未做多重比较或选择偏差校正。

`provenance` 必须可用 JSON 表达，应记录标签成熟时间、数据与模型版本、股票池、
切分、控制变量可用时间、收益口径和已有试验。
指纹只标识规范化后的相关输入，不证明 PIT、安全切分或可成交性。
不能只凭这些统计晋升策略。私有参数、面板和生成结果保留在所属研究项目的数据目录。
