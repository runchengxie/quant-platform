# Execution domain

Language: English · [简体中文](README.md)

`quant_execution_engine` provides reusable execution-domain components: target-file normalization, typed order and portfolio models, wire codecs, broker-neutral capability contracts, and deterministic simulated execution.

The public package does not provide a standalone production CLI. Production broker adapters and their commands belong to private runtime environments. Broker SDK integrations, credentials, live-trading configuration, audit storage, and production runtime are not part of this public package.

The compatibility namespace remains during migration from the former execution repository.

## Output paths

Execution audit, state, and evidence default to the user state directory under `quant-platform/execution`. If `DATA_PLATFORM_ROOT` is set, the default becomes `$DATA_PLATFORM_ROOT/quant-platform/execution`. `QUANT_PLATFORM_OUTPUT_ROOT` sets a platform output root, while the more specific `QEXEC_OUTPUTS_DIR` sets a run directory.

Precedence, from highest to lowest, is `QEXEC_OUTPUTS_DIR`, `QUANT_PLATFORM_OUTPUT_ROOT`, `DATA_PLATFORM_ROOT`, then the XDG user state directory. A path explicitly passed to a state-store or reporting API takes precedence for that call. These defaults do not create an `outputs` directory in the Git checkout.
