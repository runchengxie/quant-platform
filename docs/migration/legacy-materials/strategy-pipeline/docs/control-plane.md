# Control-plane API

`strategy-pipeline` 负责协调 owner 实现和 artifact publication，传递 reference 和
receipt，不计算 artifact 的具体内容。

## Contracts

`ArtifactRef` 用 kind、URI、digest 和 producer 标识不可变输出。`RunRequest` 携带
run ID 和输入 artifact reference。`PublicationRequest` 与 `HandoffRequest` 描述
下游交付。`RunReceipt` 记录公共结果，不暴露 owner 的异常文本。

```python
from strategy_pipeline import ArtifactRef, RunRequest, run

request = RunRequest(run_id="run-2026-01-01", inputs=())
```

所有 contract 都是不可变且经过校验的 dataclass。产出 artifact 的代码应返回
`ArtifactRef`，避免返回内存中的 domain object 或 provider client。

## 编排

公共 runner 先调用 `RunOwner`，再调用 `ArtifactPublisher`：

```python
receipt = run(request, owner=owner, publisher=publisher)
if receipt.status == "published":
    print(receipt.artifacts)
```

注入的实现抛出异常时，runner 返回经过脱敏的 `owner_failure` 或
`publication_failure` category，不把私有异常细节序列化到 receipt。

## 其他边界

使用 `publish_artifact` 接入 callable writer，使用 `publish_handoff` 接入目标
publisher。两者都会校验注入实现返回 `ArtifactRef`。

公共包不包含 provider SDK、凭证、网络 client、存储 backend、模型实现或策略 registry。
这些能力应放在使用方仓库的 adapter 后面。

## 多 owner 编排端口

需要协调多个 owner 的使用方可以通过 `control_plane.ports` 注入数据、研究、组合和
交接端口。`PipelineOwnerPorts` 只保存协议对象，`Native*OwnerAdapter` 只负责把已有
owner callable 接到控制面。公共包不会实现这些 owner 的领域逻辑。

`completed_run_receipt` 会按 `data`、`alpha`、`portfolio` 和 `artifact_handoff` 阶段
生成可序列化回执。owner 仓库可以替换适配器实现，公共控制面只依赖协议和回执结构。

目标文件中的默认 source label 是 `strategy-pipeline`。它表示控制面负责生成交接文件，
不表示控制面拥有具体策略或研究逻辑。需要自定义 source label 的使用方可以在自己的
adapter 中显式传入，不应把策略名称写入公共包。

## AFML 证据绑定

`attach_afml_evidence_to_lineage` 可以把运行目录中已生成的研究协议、组合 sizing、
风险和 HRP receipt 绑定到 `targets.json.lineage.json`。函数只写入证据文件路径和
SHA-256，不修改目标持仓语义。默认要求研究协议报告的 `level` 为 `release` 且
`status` 为 `pass`，可以通过 `require_release_protocol=False` 放宽这个要求。
