# 公开微观结构框架

本包提供可复用的事件流表示、数据集接口、模型构件、确定性训练工具和合成市场模拟器机制。

真实 L2 数据、专有标签、研究股票池、实验结果、模型晋升决策和生产配置继续保留在私有研究仓库，
不进入公开包。

迁移期间保留公开命名空间 `ticknet`：

```python
from ticknet.eventstream.model import ModelConfig, build_eventstream_model
from ticknet.eventstream.dataset import L2WindowDataset
from ticknet.simulator.matching import MatchingEngine
```

公开测试只使用确定性输入或合成输入。下游研究项目可以通过这些接口提供自己的带版本数据 manifest 和标签。
