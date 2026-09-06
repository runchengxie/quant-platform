# 接入 owner 实现

owner 仓库提供领域行为并实现公共 protocol。adapter 只负责转换公共 request、调用
owner，然后返回经过校验的 `ArtifactRef`。

```python
from strategy_pipeline import ArtifactRef, PublicationRequest, RunRequest, run


class Owner:
    def run(self, request: RunRequest) -> ArtifactRef:
        # 领域计算留在 owner 仓库。
        return ArtifactRef(
            kind="owner.result",
            uri=f"memory://runs/{request.run_id}/result.json",
            digest="sha256:replace-with-real-digest",
            producer="owner-repository",
        )


class Publisher:
    def publish(self, request: PublicationRequest) -> ArtifactRef:
        # 存储和发布策略留在使用方仓库。
        return request.artifact


receipt = run(RunRequest("example", ()), owner=Owner(), publisher=Publisher())
```

策略思想、特征构造、模型选择、组合规则、provider client、凭证和私有数据都不能
进入这个包。公共控制面应能在 clean environment 中配合 synthetic owner 和 publisher
使用。

接入 workspace 时，应在使用方的 dependency lock 中固定已审阅的 public commit
或 release，并增加一条不导入私有模块、覆盖完整 request-to-receipt 路径的集成测试。
