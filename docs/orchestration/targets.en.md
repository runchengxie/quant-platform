# Exporting target files

Language: English · [简体中文](targets.md)

The public pipeline provides `export-targets`, which converts owner-produced holdings JSON into a `quant-execution-engine.targets/v2` file. It handles file shape, market suffixes, and basic numeric validation. It does not load strategy configuration or provider data, or connect to a broker.

Input may be an array of holdings or an object with a non-empty `holdings` array:

```json
{
  "run_id": "run-20260905",
  "as_of": "2026-09-05",
  "holdings": [
    {"symbol": "600000.SH", "weight": 0.6},
    {"symbol": "000001.SZ", "weight": 0.3}
  ]
}
```

```bash
strategy export-targets \
  --holdings artifacts/holdings.json \
  --out artifacts/targets.json
```

The command also writes `targets.json.lineage.json` by default. It accepts long-only holdings with finite, non-negative weights whose total is greater than zero and no more than one. Duplicate normalized `(symbol, market)` pairs are rejected. `.SH`, `.SZ`, `.BJ`, `.XSHG`, and `.XSHE` suffixes map to `market: CN`; other symbols need an explicit market.

For China-only targets, the exported `target_gross_exposure` is `0.99`; for other or mixed markets it is `1.0`. The resulting file can be passed to `quant-execution-engine` for its own dry-run, paper, or live gates.
