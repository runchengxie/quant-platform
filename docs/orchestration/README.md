# Orchestration

Language: English · [简体中文](README.zh-CN.md)

The `strategy_pipeline` package provides reusable run control, artifact publication, quality gates, receipts, and owner-handoff contracts. Callers supply the owner logic and publication adapters; the public control plane coordinates them without defining the contents of research artifacts.

The package exports `RunRequest`, `RunReceipt`, `ArtifactRef`, `PublicationRequest`, `HandoffRequest`, and the `run`, `publish_artifact`, and `publish_handoff` functions.

See the [control-plane API](control-plane.md) for the request and receipt contracts, owner/publisher ports, failure handling, and handoff behavior.

## Responsibilities and boundaries

- Owners implement domain work and return artifact references rather than in-memory domain objects or provider clients.
- The control plane invokes the owner and publisher, validates returned `ArtifactRef` values, and emits a sanitized receipt.
- Quality gates evaluate caller-provided checks and release-protocol reports. They do not calculate strategy metrics or access data providers.
- Provider SDKs, credentials, network clients, storage backends, model implementations, and strategy registries remain outside the reusable control-plane contracts.

The installable `strategy-pipeline` CLI is registered by the root project. Its command surface includes target export, research-protocol and AFML-evidence commands, and a cashflow shadow-publication adapter.

## English documentation

- [Evaluation orchestration](evaluation.md)
- [Reference pages](reference/README.md)

## Chinese originals (translation in progress)

- [Run artifacts](output-artifacts.en.md), [output orchestration](output-orchestration.en.md), and [run summaries](output-summary.en.md)
- [Owner integration](integrating-an-owner.en.md) and [target export](targets.en.md)
- [Quality gates](operations/quality-gates.md)
- [CLI and evidence-protocol guide](evidence-protocol-cli.md) and [cashflow publication guide](cashflow-publication.md)
- [Runtime helpers](reference/runtime-helpers.md)

English companions are available for [run artifacts](output-artifacts.en.md), [quality gates](operations/quality-gates.en.md), and [runtime helpers](reference/runtime-helpers.en.md).
