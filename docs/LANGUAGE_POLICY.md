# Language policy

Language: English · [简体中文](LANGUAGE_POLICY.zh-CN.md)

`quant-platform` uses English as the canonical language for public engineering
interfaces and reusable documentation. A Chinese companion may be added for
human readers, but it must not create a second source of truth.

## Contracts and artifacts

- Python identifiers, public APIs, CLI flags, schema keys, artifact fields,
  error codes, and machine-readable metadata are English or language-neutral.
- Generated JSON, CSV, Parquet metadata, and receipts must not require a human
  language to be interpreted.
- Human-facing renderers may localize labels and prose after the underlying
  typed model or artifact has been produced.
- Locale is independent from timezone, currency, calendar, and numerical
  precision.

## Documentation

`README.md`, API documentation, specifications, ADRs, and contract definitions
are canonical in English. Chinese translations should use the `.zh-CN.md`
suffix or a clearly paired location and link back to the canonical document.
Do not maintain two independently edited copies of contract semantics.

Research assumptions, proprietary features, and strategy conclusions remain in
the private research repository. This repository documents reusable mechanisms
and public evidence only.

## Migration rule

When localizing an existing document, preserve code blocks, identifiers, file
paths, schema examples, and exact command output. Translate explanatory prose
first; defer comments and historical archives until an active entry point has a
canonical version and a linked companion.

Supported public locale identifiers are `en-US` and `zh-CN`. Implementations
must reject unknown locale identifiers rather than silently changing contract
semantics.
