# Research and execution assurance

Status: written design approved by the user on 2026-10-10; implementation plans
await review and execution-method selection. No implementation has started.

## Outcome and scope

Strengthen five existing flows: complete experiment accounting, information-time
validation, execution cost and capacity evidence, synthetic scenarios with known
truth, and recovery under interrupted publication or delivery. Each flow must
have a runnable entry point, regression tests and concise operating documentation.
Adding an unused utility or writing a checklist alone does not complete a flow.

The user requested all five improvements. Preserve existing repository ownership,
public/private boundaries and compatible entry points. Use offline synthetic
inputs for acceptance. Production deployment, real recipient messages, broker
orders, paid data acquisition and model training on locked data are outside this
implementation scope. Synthetic evidence establishes software behavior, not
investment performance or calibrated real-market costs.

## Existing implementation inspected

- `quant-research/src/strategy_research/trial_registry.py` discovers runs through
  `summary.json`; it cannot account for an attempt that produces no summary.
- The research repository already validates `trial_ledger_entry.v1`, including
  proposed/running/failed states, search families and exclusions from multiple
  testing. Reuse this contract rather than adding a competing ledger.
- `quant-deep-learning` already reserves experiments before execution, tracks
  runs in SQLite, and governs locked-test access. Preserve this independent
  registry; improve coverage and export instead of replacing it.
- `PointInTimeDataView` filters availability/event timestamps and snapshots
  caller data; temporal validation already purges overlapping label windows.
- `tca_calibration.py` reports requested-notional-weighted modeled/realized cost
  and coverage, but does not decompose signed shortfall, group observations or
  report tail costs and uncertainty. Capacity grid simulation already exists.
- Microstructure generation, replay, matching and optional Rust parity tests
  already exist. The new scenarios supplement them with explicit truth.
- Backtest workers publish result directories by rename and then persist job
  status. Existing tests cover signal failures and expired leases.
- Report delivery has content-dependent idempotency keys and successful receipts;
  business freshness follows expected trading dates. Preserve these mechanisms.

This inspection does not establish every caller's compliance. Implementation
must trace the named integrations before changing them and add acceptance tests
at those boundaries.

## Approach

Extend existing mechanisms and add versioned evidence where their current
contracts cannot express the required behavior. Alternatives are a separate
cross-project assurance service, which adds another runtime and duplicates
ownership, or documentation-only adoption, which does not enforce behavior.
The recommended approach keeps persistence with its current owner and shares
only public mechanisms or versioned artifacts.

## 1. Complete trial lifecycle

Owner: private `quant-research`; model-specific registry stays in
`quant-deep-learning`.

Add a lifecycle writer and controlled CLI wrapper in `strategy_research` using
the existing trial entry schema. Persist a proposed record before launching a
permitted research command, then running, then a terminal record. Store lifecycle
events separately from the existing one-entry-per-trial validation input; export
the latest state of each trial to the existing ledger validator. Do not silently
reinterpret repeated records as distinct trials or rewrite historical ledgers.

Require trial identity, candidate fingerprint, search family, code/data revision
and evaluation windows before execution. Identical retries are idempotent;
changed identity under the same trial ID is rejected. A command failure records
its exit code and reason. Abrupt process death leaves an unfinished attempt
visible; an explicit recovery command marks it failed with a reason. Do not
pretend hard termination can execute a finalizer.

A family report counts all eligible attempts, failed/rejected attempts and
unfinished attempts. Exclusion rules reuse the existing validator. Report
unaccounted legacy runs as unaccounted, not as completed or statistically
independent. Family counts alone are not a multiple-testing correction.

Integrate the wrapper with one existing research command and expose it as the
supported entry for other commands. In deep learning, export family/run evidence
from the existing registry and test pre-execution rejection, executor failure
and interrupted runs. Do not import private research modules across repositories.

Acceptance: failed commands without summary files remain discoverable; duplicate
IDs cannot overwrite attempts; interrupted runs remain in family counts; a
rejected result cannot be excluded because its metric is poor; current ledger
and legacy registry inputs remain usable.

## 2. Information-time and label-window assurance

Public owner: `quant-platform`; feature integration: `quant-research`;
model-window integration: `quant-deep-learning`. Data publication remains owned
by the market data provider. No provider acquisition changes are required.

Add an explicit revision-selection operation to the point-in-time view. The
caller declares identity columns, revision order and availability timestamp.
First filter at the information cutoff, then select the latest visible revision
per identity. Identical timestamps without an unambiguous declared revision
order are rejected. Preserve the current all-visible-rows read behavior.

Use the operation in one existing PIT feature materialization path and test
publication delays and later corrections through feature construction and a
synthetic backtest. Missing/naive availability timestamps continue to fail.
Reports record the information cutoff, dataset version, revision policy and
purged label count.

For deep-learning samples, exercise the existing split/label horizon path rather
than adding a platform dependency. The signal, entry and return end must remain
within the permitted split. Distinguish trading-day horizon rules from the
public calendar-day embargo parameter; do not change either implicitly.

Acceptance: a late publication is invisible before receipt; a later correction
does not change the earlier decision; reordering source rows does not change
revision selection; overlapping labels are removed through the consumer path;
non-overlapping valid inputs produce the existing results.

## 3. Cost, tail risk and capacity evidence

Public owner: `quant-platform`; research consumption: `quant-research`;
job artifact handling: `quant-backtest-runtime` only if the added result artifact
requires an explicit runtime contract extension.

Add a versioned order-level shortfall contract: order identity, buy/sell side,
decision price, requested quantity, fill quantities/prices, explicit fees,
unfilled benchmark price and benchmark time, completion time, and grouping
features such as participation/liquidity and volatility regime. Reject negative
quantities, overfills and missing unfilled benchmarks for partial orders.
Favorable execution may have negative signed shortfall; do not apply the old
non-negative cost-field rule to this new measure.

Compute signed execution deviation, opportunity cost on unfilled quantity and
fees, normalized by requested decision notional. Keep these components distinct
from non-negative modeled fee/impact assumptions. Keep the existing v1 calibration
API and output unchanged; publish new evidence under a separate version.

Summarize mean, median, empirical P95, completion ratio, observation coverage and
market-date coverage by caller-specified groups. Use a seeded date-block bootstrap
for mean uncertainty (500 resamples by default, configurable). If there are fewer
than two distinct dates, mark uncertainty unavailable. Minimum sample and coverage
requirements are explicit inputs, not universal promotion thresholds. Do not
automatically promote or modify a cost model.

Extend the existing capacity report with this evidence when available, retaining
the existing scale/participation grid and making missing evidence explicit.
Consume the report in one research evaluation entry and record it as a hashed
artifact. Deterministic synthetic fixtures compare scale, fill coverage and net
returns. Do not assert that arbitrary real strategies must have monotonic returns
as scale changes; monotonic expectations apply only to a constructed scenario.

Acceptance: hand-calculated buy/sell/partial-fill cases match; a zero-fill order
retains opportunity cost; favorable execution is representable; insufficient
sample groups cannot receive a ready recommendation; existing v1 callers pass;
capacity evidence reaches a consumer report rather than remaining an unused API.

## 4. Synthetic scenarios with explicit truth

Owner: public `quant-platform` for strategy-neutral factories and manifests;
consumers own their integration tests. Deep learning stays independently usable.

Provide deterministic, lightweight scenario artifacts for a null signal, an
industry-confounded signal, delayed/revised input, and order events with partial
fills/cancellations or sequence gaps. Each manifest declares its seed, schema,
input hashes, expected invariants and known truth. Use synthetic identifiers only.
Keep scenario generation independent of Torch/GPU/native extensions.

Null-signal acceptance checks use constructed orthogonal or paired data and
known exact outcomes, not a flaky requirement that a random Sharpe falls below a
chosen threshold. Industry scenarios check attribution/neutralization. Timestamp
scenarios drive item 2. Event scenarios drive execution bookkeeping and existing
Python/Rust equivalence tests when the optional Rust backend is installed.
Sequence gaps must be flagged as incomplete evidence, not silently repaired.

Expose a public factory/CLI plus a synthetic smoke example. Research and runtime
consume the public package or artifacts; independent deep learning tests consume
the artifact contract without importing platform implementation modules.

Acceptance: regeneration matches hashes; changing a seed changes the relevant
artifact; truth is explicit and asserted by a consumer; no credentials, network,
real data or GPU are needed; native checks clearly distinguish pass from skip.

## 5. Interrupted publication and delivery

Owners: `quant-backtest-runtime` for job publication;
`quant-intel-platform` for report delivery/freshness/recovery. Deployment runbooks
may be updated later in `quant-intel-deploy`; no scheduler or release switch is
part of this code delivery.

Use controlled failure injection in tests at persistence boundaries. For jobs,
cover result rename before success-state commit, manifest/hash failure, lease
expiry and a second recovery interruption. Published-but-uncommitted output must
not be exposed as a successful job or cause duplicate execution. Preserve the
runtime's existing conservative failure/recovery semantics unless its contract
explicitly supports adoption of a verified result.

For reports, record a durable sending intent before invoking the external sender.
If acknowledgement is missing after a crash, keep an unknown outcome. Reconcile
through provider-supported identity/receipt lookup when available. If lookup or
provider idempotency is unavailable, block automatic resend and require an
explicit operator resolution. A successful local receipt suppresses exact retries;
new content remains a distinct delivery. This is not an exactly-once guarantee.

Runbook checks distinguish expected business date, complete artifact inventory,
delivery outcome and recovery state. Exercise stale input, corrupted receipts,
restart and partial-route success using fake senders; send no real messages.

Acceptance: repeated recovery is idempotent; unknown sends are not automatically
resent; confirmed success is skipped; wrong-date input does not pass freshness;
unrelated processes/files are preserved; fault scenarios run through real local
orchestration rather than testing mocks alone.

## Delivery and verification

Implement in independently reviewable repository branches/worktrees. Start with
public scenarios, PIT and cost contracts, then research consumers, then runtime
and report recovery. Each provider must be merged before dependent consumers pin
its revision. Do not use sibling source imports or unpublished development refs.

Run failing acceptance tests before implementation, related regressions during
work, and each repository's required gates before merge. Runtime signal/resource
tests require Linux; use an available Linux environment and record its identity,
rather than calling skipped Windows tests proof of recovery. Run optional Rust
parity when its toolchain is available and disclose any remaining skips.

Keep artifacts/logs outside source trees, preserve current user changes and
locked-test controls, and retain any PR blocked by enforced checks. Delivery is
complete only when all five flows have merged implementations and consumer-level
evidence, or a specific unresolved external blocker is reported. Production
rollout remains separate from repository merge.
