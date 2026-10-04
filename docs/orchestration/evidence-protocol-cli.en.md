# Evidence and protocol CLI

Language: English · [简体中文](evidence-protocol-cli.md)

The `strategy-pipeline` command provides two entry points for research evidence:

- `research-protocol` creates a protocol-manifest template or evaluates an existing JSON/YAML manifest.
- `afml-evidence` generates sizing and strategy-risk evidence, with optional HRP returns evidence. It can also merge the generated evidence into a protocol manifest.

## Initialize or evaluate a protocol

Create a template for the chosen protocol level:

```bash
strategy-pipeline research-protocol --level exploratory --init-manifest protocol.yml
```

To evaluate a manifest, pass `--manifest` instead. The command writes a report to
`research_protocol_report.json` by default; `--output` changes that path. Strict
evaluation is enabled by default and returns a non-zero exit code when the report
does not pass. Use `--no-strict` when a failing report should still return exit code 0.

## Generate AFML evidence

Point the command at a run directory:

```bash
strategy-pipeline afml-evidence --run-dir artifacts/runs/example
```

Optional arguments set the target Sharpe ratio, evaluation period, bootstrap
sample count, random seed, and HRP returns input. Pass `--manifest` to merge the
generated evidence into an existing protocol manifest. The command writes back to
that manifest unless `--manifest-output` specifies a separate path. JSON manifests
remain JSON; other supported manifest files are written as YAML.

The CLI lives in `strategy-pipeline`. Evidence calculations are implemented by
`portfolio-backtester`; protocol manifest loading and evaluation are implemented
by `quant-market-research`. This repository provides argument parsing, file I/O,
and command orchestration around those components.
