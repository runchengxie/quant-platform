# Portfolio Construction P0 Design

## Goal

为组合构建建立一个可复用、可审计的第一阶段公共能力：在 `quant-platform` 提供严格校验的 inverse-volatility optimizer 和确定性的 no-trade 经济再平衡；在 `quant-research` 以薄适配暴露冻结的 w025/w089 recipe，不复制平台算法。

## Scope and non-goals

本切片只覆盖：

- `native.inverse_vol` optimizer backend；
- 以历史收益计算年化前波动率、按 `volatility ** -exponent` 生成偏好权重，并复用现有 box-simplex projection；
- 组合级 no-trade threshold：若目标权重与当前权重之间的半 L1 turnover 不超过阈值，则保持当前权重；否则采用目标权重；
- research-owned 的冻结 recipe `w025` 与 `w089` 及其契约测试；
- 公共 API、错误行为、诊断信息和测试。

明确不在本切片内：第三方 QP solver、alpha calibration、factor risk model、行业/风格约束、非线性 market impact、逐票 no-trade band、动态总仓位和指数对冲。

## Architecture

`quant-platform` 继续以 `PortfolioOptimizationRequest -> PortfolioOptimizerBackend -> PortfolioOptimizationResult` 为稳定边界。通用算法和输入验证留在 `portfolio_backtester`；backend-specific 参数通过 `InverseVolConfig` 注入，不污染 request 契约。

经济再平衡作为独立的纯函数 API 实现，接受 fully-invested long-only 的目标与当前权重。它只做“整笔保持或整笔采用”的 no-trade 决策，避免在预算约束下隐式重新分配导致阈值语义失真。真实执行费用仍由既有 execution simulator 负责。

`quant-research` 只保存研究结论和参数：`w025` 使用 252 日、指数 0.5、1%～3% 上下界；`w089` 使用 252 日、指数 1.0、0.5%～4% 上下界。research adapter 返回平台 backend，禁止重新实现波动率和权重投影。

## Public interfaces

### Inverse-volatility backend

```python
@dataclass(frozen=True)
class InverseVolConfig:
    lookback: int = 252
    exponent: float = 0.5
    min_periods: int | None = None


class InverseVolOptimizerBackend:
    name = "native.inverse_vol"

    def __init__(self, config: InverseVolConfig | None = None): ...
    def run(self, request: PortfolioOptimizationRequest) -> PortfolioOptimizationResult: ...
```

`min_periods=None` 表示必须有完整 lookback；显式值必须为正整数且不大于 lookback。收益窗口不足或最近窗口的某一资产波动率不是有限正数时，backend 抛出 `ValueError`，不得静默把它当成低波动资产。单资产请求直接返回 100%，但仍验证 request 的边界可行性。

### Economic rebalance

```python
@dataclass(frozen=True)
class EconomicRebalanceResult:
    weights: pd.Series
    diagnostics: Mapping[str, Any] = field(default_factory=dict)


def apply_no_trade_band(
    target_weights: pd.Series,
    previous_weights: pd.Series | None,
    *,
    min_turnover: float = 0.0,
) -> EconomicRebalanceResult: ...
```

输入必须是相同资产集合、有限、非负且总和为 1 的 fully-invested 权重；`min_turnover` 必须有限且非负。半 L1 turnover `0.5 * abs(target - previous).sum()` 小于等于阈值时返回 previous 的副本，否则返回 target 的副本。没有 previous 时直接采用 target，并在 diagnostics 标记 `previous_weights_missing`。

diagnostics 至少包含 `method`, `min_turnover`, `turnover_before`, `turnover_after`, `traded`, `previous_weights_missing`；所有值必须可 JSON 序列化。

## Failure and compatibility behavior

- 保留 `portfolio_backtester` 命名空间和既有 optimizer schema；新增类和函数从 `portfolio_backtester.optimization`/顶层公开导出。
- 不改变 EqualWeight 或 HRP 的默认行为。
- inverse-vol 的 invalid volatility、参数错误和不可行 bounds 都显式失败。
- no-trade 不修改输入 Series，不隐式排序资产，不改变权重总和。
- research adapter 对未知 recipe 名称显式失败；不引入真实数据、凭证或专有因子。

## Testing strategy

平台单元测试先覆盖：

1. inverse-vol 对较低波动资产给出更高 raw preference；
2. bounds projection 仍严格满足 min/max 且总和为 1；
3. lookback/min_periods/exponent 和零波动输入的错误边界；
4. registry/backend identity、diagnostics 和顶层导出；
5. no-trade 的 below/equal/above threshold、缺失 previous、输入不变和非法输入。

research 测试覆盖：

1. w025/w089 映射到精确的冻结配置；
2. adapter 返回 `native.inverse_vol` backend；
3. 未知 recipe 被拒绝；
4. adapter 源码不复制平台 inverse-vol 实现。

验证顺序为平台定向测试、平台全套 `ruff`/`pytest`，然后 research 定向测试、相关静态检查和完整研究测试；provider 未提交前不在 research 中引用未发布的开发路径。
