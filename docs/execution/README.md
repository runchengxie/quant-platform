# Execution interfaces

`quant_execution_engine` contributes the public execution domain: target-file
normalization, typed order/portfolio models, wire codecs, broker-neutral
capability contracts, and deterministic mock execution.

Concrete broker SDK adapters, credentials, live configuration, audit storage,
and production runtime remain private in `quant-research`.

The migrated compatibility namespace is intentionally preserved while the
workspace transitions away from the legacy execution repository.

