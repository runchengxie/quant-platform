# 同日因子冗余诊断

[English](factor-redundancy.en-US.md)

`factor_redundancy` 接收唯一的 date/symbol 多重索引数值矩阵，显式指定两端比例和
最小截面样本量，输出配对诊断、覆盖率和共同样本有效秩三个表。

Spearman 与 Top/Bottom Jaccard 使用每对信号的共同非空样本。边界并列保留，
报告实际组大小。有效秩只使用全部因子的共同样本及其 Spearman 相关矩阵，
不使用逐对缺失拼接的矩阵。常数、样本不足或显著非半正定时明确保留缺失和状态。
新增未来日期不会改变过去结果。

Participation Ratio 不是独立试验数，低相关不等于不同经济机制或组合增益。
LOO 需要在冻结流程中真实重新拟合，并登记额外的结果访问。
股票池、PIT、标签与基准仍由研究调用方负责。

完整入口为 `alpha_research.factor_redundancy.factor_redundancy(scores,
 top_fraction=..., min_cross_section=...)`。至少两个唯一命名的实数因子，
`0 < top_fraction <= 0.5`，最小截面为至少 3 的整数。返回 `pairs`、`coverage`、
`rank` 三个 DataFrame。每端至少选取 `ceil(n * top_fraction)` 个观测，并保留边界并列。
逐对样本数可能不同，比较前须检查覆盖率。复数、无穷值和重复键拒绝输入。
