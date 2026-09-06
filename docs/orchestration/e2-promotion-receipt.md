# 晋级回执

strategy_pipeline.e2_promotion_receipt 提供一个只负责落盘的回执 writer。
调用方必须先准备研究检查结果，writer 会校验回执结构，并为声明的配置、数据清单和
来源 artifact 计算 SHA-256。

writer 不判断策略是否值得晋级，也不会从输入数据推导研究结论。status 和每项检查
的状态必须由调用方明确提供。检查未完成或失败时，应保留 pending 或 failed 状态，
并在 limitations 中记录限制。

## 调用

~~~python
from pathlib import Path

from strategy_pipeline.e2_promotion_receipt import materialize_promotion_receipt

receipt = materialize_promotion_receipt(
    spec,
    workspace_root=Path("/path/to/workspace"),
    data_platform_root=Path("/path/to/data-platform"),
)
~~~

lineage.config 和 workspace 位置的来源 artifact 必须使用相对于 workspace_root
的安全路径。lineage.current_contract、data_manifests 以及 data-platform 位置的
来源 artifact 使用相对于 data_platform_root 的安全路径。

所有声明的文件都必须存在。返回值包含原始 lineage 信息和每个文件的 sha256。
写入 JSON 文件由调用方决定，公共包不会替调用方发布或覆盖文件。

## 命令行

~~~bash
python -m strategy_pipeline.e2_promotion_receipt \
  --spec receipt-spec.json \
  --workspace-root /path/to/workspace \
  --data-platform-root /path/to/data-platform \
  --output promotion-receipt.json
~~~

这个模块只依赖 Python 标准库，适合在 owner 仓库中作为通用证据落盘工具使用。
