# Reuse Qlib for bounded expression admission

The user delegated implementation of upstream-first research integration. Reuse
Qlib's real operator objects and window metadata, not a second numerical factor
engine. Keep the existing execution/data ownership and optional dependency.

Alternatives: full RD-Agent/Qlib replacement duplicates existing providers and
trial authority; a new full QBX compiler duplicates mature arithmetic operators.
Selected approach: bounded adapter around Qlib, then private RD-Agent JSON handoff.
This is a constrained admission slice, not a complete typed port-DAG compiler.

Public API: preflight_qlib_expression(expression, *, allowed_fields, context,
role='signal', label_lookahead=0) -> JSON-compatible receipt. The fixed context
binds data_revision, universe_revision, calendar_revision, execution_policy_revision,
frequency and dependency_lock_sha256. Qlib operator behavior/version is bound too.
The vocabulary is finite: Feature, Ref, Mean, Std, Sum, Min, Max, Rank, Corr, Abs,
Log and elementary +,-,*,/. Fields must be explicitly admitted; attributes,
imports, subscripts, arbitrary calls and unbounded/invalid windows are rejected.
No Python eval, data fetch, qlib.init or code execution is exposed by preflight.
Actual numerical functions and extended-window calculation remain Qlib-owned.

Signal expressions cannot request future observations. Labels can request them
only within an explicit positive horizon. A label receipt never admits a signal.
Missing Qlib yields unavailable, without substituting a homegrown evaluator.
Context identity is an exact syntactic/content identity, not semantic formula
equivalence or proof of PIT data. No node-result cache or new scheduler is added.

Acceptance: real pinned Qlib 0.9.7 in Python 3.12, ordinary and nested windows,
future signal rejection, bounded label allowance, field/code injection rejection,
context-sensitive deterministic identity, absent-dependency behavior, unchanged
native backend tests. No test market data or paid LLM is required.
