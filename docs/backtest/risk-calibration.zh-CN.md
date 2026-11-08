# 风险校准与缺失观测

语言：简体中文 · [English](risk-calibration.md)

`quant_platform.analytics.risk_calibration.audit_risk_calibration` 将显式提供的
预测均值和边际风险，与目标区间、单位完全一致的实际结果比较。不可用、陈旧、缺失和
不兼容的记录都会保留。这是回顾性的描述审计，不是时点数据读取器、未见市场检验或
真实风险认证。现有风险模型和对齐风险窗口的默认行为不变。

```python
from quant_platform.analytics.risk_calibration import audit_risk_calibration

report = audit_risk_calibration(
    forecasts,
    outcomes,
    as_of=audit_clock,
    minimum_observations=20,
)
```

## 必需证据

输入为 pandas DataFrame。时间必须明确带时区，统一转换为 UTC。数值可以缺失，
已知数值必须有限。未知收益不会变成零。空表仍需保留必需列，函数不修改输入。

| 预测列 | 含义 |
| --- | --- |
| `symbol`、`target_start`、`target_end` | 资产或因子名称，以及长度为正的目标区间 |
| `forecast_at`、`available_at` | 决策时点与该预测的可用时点 |
| `unit` | `return_fraction`、`return_bps`、`price_change:<currency>` 或 `factor:<declared-unit>` |
| `forecast_mean` | 以 `unit` 表示的预期结果。必须显式提供，包括主动采用的零均值假设 |
| `forecast_variance` 或 `forecast_volatility` | 每行最多一种已知风险。方差为单位的平方，波动率为原单位。两者缺失时保留未知状态 |
| `liquidity`、`regime` | 非空的流动性、市场状态标签。未知时可显式使用 `unknown` |

| 结果列 | 含义 |
| --- | --- |
| `symbol`、`target_start`、`target_end`、`unit` | 必须与预测完全一致的匹配键 |
| `realized` | 以声明的区间单位表示的实际结果 |
| `available_at` | 结果可用时点，不得早于观测完成时点 |
| `observation_start`、`observation_end` | 实际观测区间，用于识别陈旧端点 |

预测键还包含 `forecast_at`，因此允许多个决策预测同一区间。重复键直接报错，不会挑选
有利版本。调用方必须先处理结果修订。区间长度按 UTC 实际纳秒计算，不推断交易日数。
单位只按声明校验，不认证数据供应方语义。不会自动年化、换汇、归一化因子或缩放期限。
人民币价格变化不能标成小数收益。

方差配对要求预测在决策前可用，决策不晚于区间起点和 `as_of`，区间完成及结果可用均
不晚于 `as_of`。实际观测起止必须等于目标起止。同一代码和起点存在其他结果但没有
完全一致的键时，标记为 `incompatible_outcome`。所有预测保留在 `rows`，并给出
`issues` 与 `paired`。所有结果保留在 `outcomes`，包括未匹配记录，并给出
`match_status`、`matched_forecasts` 和自身的可用性、缺失问题。键匹配不等于有效配对。

这是回顾审计，原始不可用数值仍会显示，包括 `matched_realized`。消费者必须检查
`paired` 和可选比较的状态，不能把整张表当成策略当时可见的信息集。输出派生列名
`paired`、`issues`、`horizon_ns`、`residual`、`squared_residual`、
`predicted_variance`、`matched_realized`、`exposure_status`、`interval_status`、
`interval_covered` 不允许用作预测输入列名。其他附加预测列保留原名和原值。

## 可比口径与样本证据

`summary` 按完全一致的 `unit` 和 `horizon_ns` 分组，`cohorts` 再按 `liquidity`、
`regime` 分组，保留全部缺失的低流动性组。覆盖率为有效方差配对数除以该组全部预测数。
预测方差和实际残差平方使用完全相同的配对行：

- `residual = realized - forecast_mean`。
- `predicted_variance = forecast_variance`，或仅将 `forecast_volatility * forecast_volatility` 计算一次。
- `realized_squared_residual = mean(residual * residual)`。
- `variance_ratio = mean(residual * residual) / mean(predicted_variance)`。

这些是描述性的条件二阶矩诊断，不是无偏方差估计或完整协方差校准。已知的非零预测均值
会先扣除。重复决策和不同资产仍按行参与点估计，相应的依赖计数单独显示。不同单位或
不同期限不会混入同一个数值均值。

`tail_observations` 仅计正方差配对，`two_sigma_exceedances` 严格计算
`abs(residual) > 2 * sqrt(predicted_variance)`，`two_sigma_rate` 使用同一尾部样本分母。
这不代表高斯分布下的 95% 覆盖率。零方差配对仍参与二阶矩诊断，非零残差另记为
`zero_variance_nonzero_residuals`。平均预测方差为零时比值未知。覆盖率或尾部样本
分母为空时，比率和超出次数均为未知，不会输出看似正常的零。无法用有限浮点数表示的
计算会明确报错，正值计算也不能无声下溢成精确的零。均值按尺度归一化后计算，避免
不必要的求和溢出或过早下溢。

合成例中，方差 `[1, 1, 4, 4]`、零均值、结果 `[1, -3, 2, -6]` 对应平均预测方差
`2.5`、平均残差平方 `12.5`、比值 `5`，四个正方差配对中两次超出。去掉最后两个
结果后，平均预测方差为 `1`，平均残差平方为 `5`。缺失的高方差预测仍进入覆盖率
分母，不会只进入其中一个二阶矩的分母。

每组报告名义 `paired_observations`、不按资产或决策重复计数的
`distinct_target_intervals`，以及 `nonoverlapping_target_intervals`。后者按最早结束
顺序，在半开区间 `[start, end)` 中求最大不重叠集合。它用于提示依赖，不是独立样本
估计。两天中六十条相关资产记录只算两个目标区间。四个每天起始、持续两天的区间有
四个不同区间，但最多两个互不重叠区间。

最小样本数必须是正整数，默认 20，在每个可比单位、期限组内分别检查。不同区间数或
不重叠区间数不足时，状态分别为 `insufficient_target_intervals` 或
`insufficient_nonoverlapping_intervals`。满足数量门槛后仍只标记
`descriptive_only_independence_unverified`。总体状态保留任一组的不足，各细分组也有
自身状态。`independence_status="unverified"` 和
`effective_independent_observations=None` 始终成立。不重叠不会消除序列、共同因子或
选择依赖，不会据此编造置信区间或统计功效保证。

## 可选的已提供敞口与预测区间

敞口比较使用预测中的 `target_exposure`、`exposure_unit`、`exposure_source`、
`exposure_available_at`，以及结果中的 `actual_exposure`、`exposure_unit`、
`exposure_source`、`exposure_observed_at`、`exposure_available_at`。目标敞口必须
在决策前可用。实际敞口观测须位于目标区间内，允许端点，可用时点不早于观测且不晚于
`as_of`。两侧单位须为完全相同的非空标签，不会从收益或协方差推断因子敞口。

`exposure_comparison` 保留目标值、实际值、来源、时点和状态，并给出
`signed_gap = actual - target` 与 `absolute_gap`。各汇总和细分组的
`exposure_observations` 统计有效比较数。缺失值、单位不符、证据缺失、不可用或越界
观测都使差值保持未知。不同敞口单位不会混算平均差值。敞口比较独立判断资格，风险
缺失不会抹去有效敞口差值，敞口缺失也不会使有效方差配对失效。未提供敞口列时，可选
表为 `None`，有效计数为零。

显式预测区间使用预测中的 `prediction_lower`、`prediction_upper`、`prediction_unit`、
`prediction_source`、`prediction_available_at`。上下界必须有限、有序、与结果单位
完全一致，并在决策前可用。可选的 `prediction_nominal_level` 必须严格介于 0 与 1。
未提供时不推断名义概率。实际结果仍须满足相同的可用性和观测区间检查。

`prediction_intervals` 逐行保留上下界、来源、可用时点、名义覆盖水平、状态和包含
端点的 `covered = lower <= realized <= upper`。汇总的 `interval_observations`、
`interval_covered`、`interval_coverage` 仅使用有效区间与结果。缺失区间或结果证据
使覆盖率未知。这些比较不要求方差或均值证据，也不会从标准差推导区间。混合名义水平
逐行保留，合并后的描述比例不代表某一个名义水平的校准结果。未提供上下界时表为 `None`。

## 已提供协方差的秩与来源

可选预测列 `raw_covariance`、`covariance_labels`、`covariance_unit`、
`covariance_available_at`、`covariance_source` 分别提供可检查的矩阵值、唯一非空维度
标签、严格为 `<unit>^2` 的单位、决策前的可用时点和调用方来源标识。可选的
`shrunk_covariance` 沿用相同标签与单位。矩阵须有限、方形、对称，并在随矩阵尺度变化
的浮点容差内半正定。`rank_diagnostics` 使用 NumPy 默认秩容差计算原始矩阵和所提供
收缩矩阵的秩，报告维度。即使收缩矩阵满秩，原始秩不足也会保留。

没有原始矩阵，或仅提供秩数字时，秩诊断不可用。未来证据不能支持秩。已提供但不完整
或无效的矩阵契约会报错。这里不验证拟合样本、收缩系数或变换，不处理不同单位的因子
混合矩阵，也不检验经济协方差或实际跨资产协方差。半正定和满秩都不能证明校准有效。

`input_digest` 对 `risk-input.v2` 规范化、带类型标记的输入表示求摘要。有限二进制浮点数
使用精确整数比，整数按十六进制编码，相邻值与很小的值不会被十进制舍入合并。嵌套矩阵
单元格使用同样的表示。整数、十进制数、文本、布尔值、缺失标记、字节和时间都有明确
类型标记。带时区时间按纳秒精度统一到 UTC，不保留 NaN 的底层载荷位。解析值相同的
列表、元组和 NumPy 数组使用同一种序列表示。映射键顺序、列顺序和 pandas 行索引不
影响摘要，记录顺序、空表结构和解析值仍被绑定。不支持的任意对象不会退化成字符串。
此次序列化版本会改变旧摘要，需要同时记录代码版本。它不代表原始文件字节摘要、供应方
认证或经济真实性证明。调用方清单仍须绑定
原始来源字节、模型与拟合版本及时间、代码与消费者版本、单位语义和来源记录。
`provenance_status="caller_asserted"`、`real_calibration="unavailable"`、
`certified=False` 始终显式保留。看过的历史样本仍是已见样本。独立的后续观测和有依据的
聚类不确定性需要研究层另行提供证据。

合成验收见 [`tests/test_risk_calibration.py`](https://github.com/runchengxie/quant-platform/blob/main/tests/test_risk_calibration.py)。
另见[风险模型内核](../risk-model-kernel.zh-CN.md)和[成本证据](transaction-cost-evidence.zh-CN.md)。
