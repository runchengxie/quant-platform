# 稀疏因子风险模拟组合优化

[English](sparse-signed-optimization.md)

`quant_platform.portfolio.sparse_signed_optimization` 面向使用
`B F B.T + diag(D)` 风险模型的大规模合成组合。安装 `quant-platform[sparse]`，
并显式选择 `SparseSignedOptimizer(backend="osqp")`。
[现有稠密接口](signed-paper-optimization.zh-CN.md)保持原有行为。

`SparseSignedOptimizationRequest` 沿用稠密请求的资产、成本、约束因子、标量、
持有期、时间戳和假设字段，将 `covariance` 替换为三个输入：

| 字段 | 要求 |
| --- | --- |
| `risk_loadings` | 资产×风险因子 DataFrame B。因子名称为唯一非空字符串，因子数少于资产数 |
| `factor_covariance` | 小型对称半正定 DataFrame F。两个轴与 B 的列完全一致 |
| `specific_variance` | 非负有限 Series D。资产标签及顺序完全一致 |

因子协方差采用严格校验：F 必须完全对称，小型矩阵计算得到的全部特征值都须非负。
不设置负特征值容差，也不自动对称化或截断。较大的风险载荷会放大很小的偏差。
校验、QP 及方差回执使用同一个 F，调用者须提供已经有效的因子协方差。

风险因子与用于暴露约束的 `factor_loadings` 相互独立。所有资产 Series、两个载荷
矩阵的资产索引必须完全一致。收益、F、D 和成本都覆盖声明的 `horizon_days`，
单位为 `horizon_decimal`。时间必须是带时区的 pandas Timestamp，信息时间不能
晚于决策时间。历史可得性与估计口径仍由调用者负责。

```python
from quant_platform.portfolio.sparse_signed_optimization import (
    SparseSignedOptimizer,
)

solver = SparseSignedOptimizer(backend="osqp", max_iter=100_000,
                               time_limit=10.0, tolerance=1e-9)
result = solver.solve(request)  # SparseSignedOptimizationRequest
next_result = solver.solve(next_request)
```

目标是最小化 `risk_aversion * variance / 2 - expected_return + trade_cost +
borrow_cost + holding_cost`。返回现有 `SignedOptimizationResult`，按实际权重计算
成本及交易净资产绝对额之和（不除以二），始终包含 `paper_only=True` 和
`executable=False`。总敞口是上限，零敞口也是有效的非投资解。

CSC 稀疏规划包含权重、交易绝对额、持仓绝对额、空头持仓和风险暴露辅助变量，
通过 `risk_exposure = B.T @ weights` 连接因子风险。Hessian 仅包含 D 和 F 的
上三角，不生成资产×资产协方差。存储量取决于载荷非零元、资产数、约束载荷非零元
和小型因子协方差，不随资产数平方增长。

保留一个求解器可连续求解。仅在标签、约束名称及实际 CSC 非零模式一致时更新数值，
并复用 OSQP 原始及对偶变量热启动。维度、标签、因子约束名称或非零模式改变时
重建。数值从零变成非零也可能使复用失效。`structure_stats` 提供建模和更新次数、
矩阵非零元、变量及约束数。这些统计不代表数值分解复用或加速保证。求解器可变，
不能用于并发调用。

只接受 OSQP 精确的 `solved` 状态，并独立重算实际资产上下界、总净敞口、约束
因子及全部辅助和等式约束，最大违反量不得超过 `1e-7`。迭代上限、超时、精度不足
或数值错误返回 `numerical_failure`，不提供权重或经济评分。原始问题不可行证书
返回 `infeasible`。不会自动切换求解器。大组合的小误差可能在总净敞口上累积。
独立检查拒绝结果时，可以显式收紧 `tolerance`。多重最优解可能具有不同权重，
冷热启动应比较目标值及约束违反量。

运行 `PYTHONPATH=packages/platform/src uv run --extra sparse python
scripts/benchmarks/sparse_signed_qp.py`，可获得 100/500/1000 资产、每组重复三次的
合成冷热启动测量。将 JSON 重定向到项目数据目录。输出包含软件、构建和线程信息、
CSC 非零元、耗时及独立冷启动的目标值差异。测量仅代表当前机器，不保证时延或
内存。输入输出不提交到公开源码库。接口依据
[OSQP 官方 Python 文档](https://osqp.org/docs/interfaces/python.html)。
