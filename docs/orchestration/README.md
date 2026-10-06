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

- [Evaluation orchestration](evaluation.md) and [control-plane API](control-plane.md)
- [E2 promotion receipt](e2-promotion-receipt.en.md)
- [Cashflow shadow publication](cashflow-publication.en.md)
- [Run artifacts](output-artifacts.en.md), [output orchestration](output-orchestration.en.md), and [run summaries](output-summary.en.md)
- [Owner integration](integrating-an-owner.en.md), [target export](targets.en.md), and [evidence and protocol CLI](evidence-protocol-cli.en.md)
- [Operations overview](operations/README.en.md) and [quality gates](operations/quality-gates.en.md)
- [Development and publication checks](development.en.md), including the [Publication audit](publication-audit.en.md) historical snapshot
- [Reference pages](reference/README.md), including [CLI helpers](reference/cli-helpers.md), [configuration](reference/configuration.md), and [runtime helpers](reference/runtime-helpers.en.md)

The [localization status](../LANGUAGE_MIGRATION_STATUS.md) tracks the remaining translation work. Paired pages link to their Chinese counterparts at the top.
