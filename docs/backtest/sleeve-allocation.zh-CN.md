# 共用账户的策略分配与未完成退出

语言：简体中文 · [English](sleeve-allocation.md)

<span id="_1"></span>
<span id="_2"></span>
<span id="_3"></span>
<span id="_4"></span>

本页保留原链接。当前实现、契约和限制见 [Engine 文档](https://runchengxie.github.io/quant-backtest-engine/backtest/sleeve-allocation.zh-CN/)。

Platform 0.2.0 支持 Python 3.12 和 3.13，使用已合并提交 `51ab1e8cb2267d938a0681b81f2419d504ed91cc` 的 Engine Core 0.2.0 和 SDK 0.3.0。两者固定到同一 VCS 提交，无需发布到 PyPI。分钟执行、纸面账户、资源预留、执行规划及确定性撮合、回放和冲击估计由 Engine 维护。兼容模块导出相同的 Core 对象。待成交分配适配器保留 Platform 的完整稀疏风险校验和原优化结果。OSQP、统计风险、研究校准、`pool_sleeves`、日频回测和模型训练仍由 Platform 维护。别名至少保留两个次版本周期，并等待所有登记的受支持使用方迁移完成。

可选原生发行包仅由 Engine 提供，安装 wheel 后必须显式选择 `backend="rust"`，没有静默回退。原生后端缺少逐笔成交证据，冲击估计会在状态修改前抛出 `NotImplementedError`。生成器和 `sqrt_law` 仍为 Platform 使用方。合成诊断斜率不代表已校准的市场规律。账户原始 schema 2 和 `execution-state.v2` 标识迁移后的状态所有者。旧检查点必须保留原先固定的完整 Platform、Runtime、Go 与依赖环境，不转换或重新绑定。

[历史源码](https://github.com/runchengxie/quant-platform/blob/7a618bddd8fdeee5dbe37fe5b54a9698e0de5355/docs/backtest/sleeve-allocation.zh-CN.md)
