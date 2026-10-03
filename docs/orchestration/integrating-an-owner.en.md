# Integrating an owner implementation

Language: English · [简体中文](integrating-an-owner.md)

An owner repository supplies domain behavior and implements the public protocol. Its adapter converts public requests, calls the owner, and returns a validated `ArtifactRef`.

```python
from strategy_pipeline import ArtifactRef, PublicationRequest, RunRequest, run


class Owner:
    def run(self, request: RunRequest) -> ArtifactRef:
        return ArtifactRef(
            kind="owner.result",
            uri=f"memory://runs/{request.run_id}/result.json",
            digest="sha256:replace-with-real-digest",
            producer="owner-repository",
        )


class Publisher:
    def publish(self, request: PublicationRequest) -> ArtifactRef:
        return request.artifact


receipt = run(RunRequest("example", ()), owner=Owner(), publisher=Publisher())
```

Keep strategy ideas, feature construction, model selection, portfolio rules, provider clients, credentials, and private data outside this package. The public control plane should run in a clean environment with synthetic owner and publisher implementations.

When integrating from a workspace, pin a reviewed public commit or release in the caller's dependency lock. Add an integration test that exercises the complete request-to-receipt path without importing private modules.
