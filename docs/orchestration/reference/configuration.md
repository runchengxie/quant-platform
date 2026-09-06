# 配置解析

`strategy_pipeline.config` 提供公共配置解析能力，包括 YAML 文件读取、包内配置读取、`extends` 继承、别名和嵌套字典合并。

```python
from strategy_pipeline.config import resolve_config

resolved = resolve_config(
    "experiment",
    aliases={"experiment": "experiment.yml"},
    search_paths=["configs"],
)
config = resolved.data
```

公共模块不定义具体策略预设，也不约定某个 workspace 的目录结构。调用方可以通过 `aliases` 和 `search_paths` 注入自己的配置布局。
