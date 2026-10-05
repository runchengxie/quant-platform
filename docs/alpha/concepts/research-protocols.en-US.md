# Research Protocols

Language: English · [简体中文](research-protocols.md)

> Status: active  
> Owner: quant-market-research  
> Last verified: 2026-10-05  
> Source of truth: yes  
> Superseded by: n/a

`alpha_research.research_protocols` defines evidence policies for exploratory, candidate, and release work. The protocol checker validates a submitted manifest, referenced files, hashes, and selected fields. It does not independently prove that a study is unbiased, reproducible, or economically sound. See the [protocol CLI reference](../../orchestration/evidence-protocol-cli.en.md) for command syntax.

## Evidence levels

| Level | Required evidence | Purging policy |
| --- | --- | --- |
| `exploratory` | Published data contract, reproducible run, and trial registry | Event-window purging is not required; fallback is allowed. |
| `candidate` | Exploratory evidence plus feature evidence, a weak-model baseline, walk-forward, final OOS, CPCV, costs/turnover/capacity, exposure screen, and negative controls | The manifest must report `event_window` mode, at least 95% event-window coverage, and no fallback. |
| `release` | Candidate evidence plus DSR, PBO or an explained `insufficient_evidence` result, scenario backtest, candidate freeze, paper/shadow evidence, sizing receipt, strategy-risk report, and operator approval | The manifest must report `event_window` mode, at least 99% coverage, and no fallback. |

These coverage thresholds are checked against values in the manifest; the checker does not calculate event windows or coverage itself. For PBO, `insufficient_evidence` is accepted only with a non-empty reason.

## Manifest and checks

Initialize a template or evaluate an existing manifest:

```bash
strategy-pipeline research-protocol \
  --level candidate \
  --init-manifest artifacts/reports/candidate_protocol.yml
```

Each evidence entry uses fields such as:

```yaml
status: missing
path: null
sha256: null
notes: Evidence description
```

For artifact-backed evidence, `status: pass` is not enough. The checker resolves `path` relative to the manifest, requires the file to exist, and verifies its SHA-256. Operator approval records `approved_by` and `approved_at`. Use `--manifest` to evaluate a file; strict mode is on by default and exits non-zero when the report fails. The default report path is `research_protocol_report.json`; `--output` changes it.

Save a release report inside its run directory when a handoff gate will consume it:

```bash
strategy-pipeline research-protocol \
  --level release \
  --manifest artifacts/reports/release_protocol.yml \
  --output artifacts/runs/example/research_protocol_report.json
```

## Generate sizing and risk evidence

Use `strategy-pipeline afml-evidence` on a completed run directory containing `backtest_net.csv` (`period_end`, `net_return`), `backtest_gross.csv` (`period_end`, `gross_return`), `backtest_turnover.csv` (`period_end`, `turnover`), and either `positions_current_live.csv` or `positions_current.csv` (a `symbol` or `ticker` column plus `weight`):

```bash
strategy-pipeline afml-evidence \
  --run-dir artifacts/runs/example \
  --target-sharpe 1.0 \
  --evaluation-years 2 \
  --bootstrap-samples 2000 \
  --manifest artifacts/reports/release_protocol.yml \
  --manifest-output artifacts/reports/release_protocol.with_afml.yml
```

The command writes `sizing_receipt.json`, `strategy_risk_report.json`, and `afml_evidence_fragment.json`. With `--hrp-returns`, it also writes `hrp_weights.csv` and `hrp_receipt.json`. The return matrix must contain a date column followed by at least two synchronized return series. The command can merge generated evidence into a protocol manifest; if `--manifest-output` is omitted, it overwrites the input manifest.

## Generate AFML evidence during a pipeline run

The pipeline can generate the same sidecars after writing run outputs:

```yaml
research_protocol:
  generate_afml_evidence: true
  target_sharpe: 1.0
  evaluation_years: 2.0
  bootstrap_samples: 2000
  random_state: 7
  hrp_returns: artifacts/reports/sleeve_returns.csv
  require_release_report: true
```

`generate_afml_evidence` defaults to `false`. `hrp_returns` is optional. `require_release_report` makes the live-operations/export handoff gate require a passing `research_protocol_report.json` in the run directory. It does not change holdings, weights, or orders.

Protocol reports are evidence for a research handoff. A passing report does not replace human review of the underlying methods and results.
