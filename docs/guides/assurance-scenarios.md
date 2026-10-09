# Synthetic assurance scenarios

Use these small fixtures to check behavior with declared truth before evaluating
real research. They require no provider credentials, network, GPU or native wheel.

```bash
uv run python -m quant_platform.scenarios null_signal --seed 7 --output /external/data/null-signal
```

The output directory must be new. Its manifest uses `quant.assurance-scenario.v1`
and records the seed, CSV input hashes/types and expected invariants. The reader
checks identity, containment, file hashes and shapes before returning data.

```python
from pathlib import Path
from quant_platform.scenarios import read_scenario

bundle = read_scenario(Path("/external/data/null-signal/manifest.json"))
signals = bundle.frames["signals"]
print(bundle.truth)
```

Available scenarios are `null_signal` (constructed orthogonal predictions and
returns), `industry_confound` (sector-only prediction), `delayed_revision`
(availability and later correction), `partial_fill` (ledger and shortfall truth)
and `sequence_gap` (observed missing channel sequence).

Consumer tests exercise neutralization, execution accounting and event provenance.
A contiguous observed subsequence does not establish a complete exchange feed:
filtering, resets and provider conventions still matter. Python/Rust replay parity
requires the optional native wheel; unavailable native tests are skipped explicitly.
Synthetic statistical or cost behavior is not evidence of real strategy performance.

## Latest visible revisions

`PointInTimeDataView.at(clock).read_latest(name, identity_cols=[...],
revision_col='revision')` selects only available rows, then the latest availability
and caller-declared comparable revision per identity. Unknown keys and identical
identity/availability/revision ties fail. Numeric revisions sort numerically;
string revisions sort lexically, so supply an ordered revision field rather than
an opaque identifier. The original `read(name)` still returns all visible rows.

Date-only disclosure metadata does not supply an intraday publication time. Keep
its documented conservative date policy separate from timestamp-aware reads.
