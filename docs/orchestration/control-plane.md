# Control-plane API

Language: English · [简体中文](control-plane.zh-CN.md)

The `strategy_pipeline` control plane coordinates caller-provided owner logic and artifact publication. It passes artifact references and receipts; it does not calculate artifact contents.

## Contracts

`ArtifactRef` identifies an immutable output with `kind`, `uri`, `digest`, and `producer`. `RunRequest` carries a run ID and input artifact references. `PublicationRequest` and `HandoffRequest` describe publication and downstream delivery. `RunReceipt` records the public result without exposing owner exception text.

```python
from strategy_pipeline import ArtifactRef, RunRequest, run

request = RunRequest(run_id="run-2026-01-01", inputs=())
```

The contracts are frozen dataclasses with validation. Artifact-producing code should return an `ArtifactRef`, not an in-memory domain object or provider client.

## Run and publish

The runner calls `RunOwner` first and `ArtifactPublisher` second:

```python
receipt = run(request, owner=owner, publisher=publisher)
if receipt.status == "published":
    print(receipt.artifacts)
```

If an injected implementation raises, the runner returns a sanitized `owner_failure` with the fixed message `owner execution failed`, or `publication_failure` with `artifact publication failed`. Private exception details are not serialized into the receipt.

Use `publish_artifact` to adapt a callable writer and `publish_handoff` to adapt a destination publisher. Both validate that the injected implementation returns an `ArtifactRef`.

The public package does not provide provider SDKs, credentials, network clients, or storage backends. Put those integrations behind adapters in the consuming repository.

## Multi-owner ports

Consumers that coordinate multiple owners can inject data, research, portfolio, and handoff ports through `control_plane.ports`. `PipelineOwnerPorts` stores protocol objects; each `Native*OwnerAdapter` connects an existing owner callable to the control plane. The public package does not implement those owners' domain logic.

`completed_run_receipt` produces a serializable receipt with `data`, `alpha`, `portfolio`, and `artifact_handoff` stages. An owner repository can replace the adapters; the public control plane depends only on protocols and receipt structures.

The default source label in target files is `strategy-pipeline`. It identifies the control plane as the component that generated the handoff file; it does not mean the control plane owns the strategy or research logic. Consumers that need another source label can pass it in their adapter rather than adding a strategy name to the public package.

## AFML evidence binding

`attach_afml_evidence_to_lineage` can bind already-generated research-protocol, portfolio-sizing, risk, and HRP receipts from a run directory to `targets.json.lineage.json`. It records evidence paths and SHA-256 values without changing target-holdings semantics. By default, the research-protocol report must have `level: release` and `status: pass`; callers can disable that requirement with `require_release_protocol=False`.
