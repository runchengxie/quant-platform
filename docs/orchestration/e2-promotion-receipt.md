# 晋级回执

语言：简体中文 · [English](e2-promotion-receipt.en.md)

`strategy_pipeline.e2_promotion_receipt` 模块负责校验回执规格并生成结构化结果。
输出采用 `strategy_promotion_evidence.v2` schema，并保留调用方提供的
`strategy_id`、`profile_id`、`review_id`、`generated_at`、`status`、`research_window`、
`checks` 和 `limitations`，同时包含经过校验的 `lineage` 数据。

回执 `status` 必须由调用方提供，且只能是 `passed`、`failed`、`pending`、`diagnostic`
或 `superseded`。`checks` 必须是非空对象。检查结果由调用方提供，模块会原样保留，
不会替调用方计算或重新解释。检查未完成或失败时，应记录对应状态，并在
`limitations` 中说明限制。模块不判断策略是否值得晋级，也不会从输入数据推导研究结论。

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

`lineage.config` 和工作区中的来源文件必须使用相对于 `workspace_root` 的安全路径。
`lineage.current_contract`、`data_manifests` 以及数据平台中的来源文件必须使用相对于
`data_platform_root` 的安全路径。

`research_window` 必须包含非空的 `configured_start_date` 和 `end_date` 字符串。模块
只检查字段非空，不解析日期语义。`lineage.repositories` 中每个 Git SHA 必须是 40 位小写
十六进制字符，且 `producer_repository` 必须出现在该映射中。`source_artifacts` 必须是非空列表，
`data_manifests` 可以为空。

所有声明的文件都必须存在。返回值包含原始 `lineage` 信息和每个文件的 SHA-256。
Python 函数只返回结构化数据，不写 JSON 文件。命令行会将结果写入 `--output` 指定路径并创建父目录。若目标文件已存在，当前实现会覆盖它，调用前请确认输出路径。

## 命令行

~~~bash
python -m strategy_pipeline.e2_promotion_receipt \
  --spec receipt-spec.json \
  --workspace-root /path/to/workspace \
  --data-platform-root /path/to/data-platform \
  --output promotion-receipt.json
~~~

这个模块只依赖 Python 标准库，适合放在策略所有者仓库中作为通用证据记录工具。回执状态由调用方提供，模块不会判断策略是否应当晋级。
