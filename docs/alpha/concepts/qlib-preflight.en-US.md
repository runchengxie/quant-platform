# Reuse Qlib operators with bounded expression admission

[简体中文](qlib-preflight.zh-CN.md)

`alpha_research.qlib_preflight.preflight_qlib_expression` constructs real Qlib
operator objects and asks them for extended-window metadata. It returns an
ordinary JSON receipt, not a framework object. It does not call qlib.init, fetch
data, run a model, cache numerical results or execute generated Python.

```python
receipt = preflight_qlib_expression(
    "Mean(Ref($close, 1), 5)",
    allowed_fields=["close"],
    context={
        "data_revision": "synthetic-v1",
        "universe_revision": "fixed-v1",
        "calendar_revision": "sessions-v1",
        "execution_policy_revision": "next-session-v1",
        "frequency": "day",
        "dependency_lock_sha256": dependency_lock_sha256,
    },
)
```

The context has exactly those six nonempty fields. The lock digest is a
lowercase SHA-256. It is caller-declared provenance, not independent verification
of installed dependencies or historical data. The root identity binds normalized
syntax, allowed fields, context, role/horizon, adapter schema and Qlib version.
Whitespace normalizes away. This is syntactic/content identity, not equivalence
of arbitrary formulas or an effective statistical search count.

The finite vocabulary is Feature, Ref, Mean, Std, Sum, Min, Max, Rank, Corr, Abs,
Log and +, -, *, /. Field names must be on the explicit allowlist. Qlib owns the
operator implementations; the adapter uses Qlib's field translation and directly
constructs registered classes from a bounded syntax tree, without Python eval.
Arbitrary attributes, imports, subscripts, comprehensions, unknown operators,
keyword arguments and expanding/unbounded windows are not admitted. Expressions
are limited to 4096 characters and 256 syntax nodes. Rolling windows are positive
integers through 4096. Ref allows nonzero integers from -4096 through 4096.
Extended left/right windows over 65536 observations are not admitted.

Default role is signal with zero future access. A negative Ref is permitted
only for role=label within an explicitly supplied label_lookahead (0..4096).
This is a label expression contract, never permission to use that label as a
predictor. `admitted` only covers the registered expression/window boundary.
`pit_verified` remains false: upstream window metadata cannot prove field
publication times, universe vintages, processor fit windows or executable prices.
Run the owner's data/timing/evidence gates separately.

Missing pyqlib returns unavailable, not a local numerical fallback. The
repository lock resolves pyqlib 0.9.7, whose available wheel requires Python 3.12
for the acceptance environment used here. Native paths remain optional-import
safe on Python 3.13. Other Qlib versions need their own acceptance check.

## Why not replace the workspace?

Reuse RD-Agent for proposing/implementing candidates in an isolated runtime and
Qlib for its tested expression machinery. Data vintages, execution/accounting,
complete trial denominators and locked-window governance remain with existing
owners. Generic DAG caching, tracking UIs and a full QBX compiler are separate
choices, not prerequisites for this small integration. No new scheduler,
calculation engine or experiment registry is introduced.

The current legacy Qlib trainer adapter still calls xgboost.train directly and
its dataset adapter performs local qlib-style normalization. Their names do not
establish Qlib DataHandlerLP/XGBModel parity. See the [backend status](framework-backends.en-US.md)
for the remaining full-support conditions. This admission feature does not
silently upgrade that backend's support claim.

Sources: [Qlib v0.9.7 expression provider](https://github.com/microsoft/qlib/blob/v0.9.7/qlib/data/data.py),
[operators](https://github.com/microsoft/qlib/blob/v0.9.7/qlib/data/ops.py),
[RD-Agent](https://github.com/microsoft/RD-Agent).
