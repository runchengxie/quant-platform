# 公开微观结构框架

本包提供事件流表示、数据集接口、模型构件、确定性训练工具和合成市场模拟器。

真实 L2 数据、专有标签、研究股票池、实验结果、模型晋升决策和生产配置继续保留在私有研究仓库，
不进入公开包。

Python 接口位于 `ticknet` 命名空间：

```python
from ticknet.eventstream.model import ModelConfig, build_eventstream_model
from ticknet.eventstream.dataset import L2WindowDataset
from ticknet.simulator.matching import MatchingEngine
```

Python 是默认模拟后端。Rust 扩展可选提供订单簿撮合、批量回放和事件排序，需单独构建和安装。安装步骤、差分测试和合成基准见[Rust 内核开发说明](../development/microstructure-rust.md)。

公开测试只使用确定性或合成输入。下游项目可以通过这些接口接入自己的版本化数据 manifest 和标签。真实 L2 数据、研究股票池、实验结果和晋升决策由私有研究项目管理。
