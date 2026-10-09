# Recovery Assurance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify conservative job publication and prevent unknown-outcome automatic resends.

**Architecture:** Fault injection reaches actual persistence boundaries. Existing job failure/lease policy stays conservative; delivery intents distinguish confirmed success from ambiguous outcome.

**Tech Stack:** SQLite, fake external senders, real local orchestration, Linux signal tests.

**Spec:** [Approved design](../specs/2026-10-09-research-assurance-design.md).

## Global Constraints

The [master plan](2026-10-09-research-assurance.md) applies. No real messages/scheduler changes. Unknown external outcome is not exactly-once delivery or proven failure.

## Review Focus

- Rename before state commit cannot advertise successful job (Task 1).
- Interrupted repeated recovery preserves unrelated files/processes (Task 1).
- Send success then acknowledgement failure blocks resend (Task 2).
- Partial-route success cannot duplicate confirmed targets (Task 2).
- Corrupt receipt/wrong business date fails conservatively (Task 3).

### Task 1: Linux worker publication faults

**Files:** quant-backtest-runtime: create tests/test_publication_faults.py; extend tests/test_worker_failures.py; modify src/backtest_runtime/worker.py, jobs.py and results.py only for demonstrated failures; update docs/operations.md.

**Interfaces:** Existing request/manifest/status/lease interfaces, no new adoption-of-success semantics.

- [ ] Test actual rename-before-status failure, stale worker publication, corrupt manifest/hash, repeated recovery, second cleanup interruption and preservation of unrelated files/processes. Same completed idempotency key cannot execute twice.
- [ ] Run uv run --locked pytest tests/test_worker_failures.py tests/test_publication_faults.py -q on Linux; establish failing/new cases.
- [ ] Fix only uncovered races and cleanup boundaries using existing conservative lease failure policy; never expose uncommitted output as successful.
- [ ] Pass Linux full static/coverage tests and scripts/smoke_backtest.py on required Python 3.12/3.13 CI. Retain recoverable PR if unavailable.
- [ ] Commit: test: exercise worker publication crash boundaries.

### Task 2: Durable intents and explicit resolution

**Files:** quant-intel-platform: create src/a_share_daily/delivery/intents.py and tests/a_share_daily/test_delivery_intents.py; modify delivery/routes.py, state.py, report_delivery.py and tests/a_share_daily/test_delivery_idempotency.py.

**Interfaces:** DeliveryIntentStore(root: Path); begin(key: str, *, route: str, target_hash: str, artifact_sha256: str) -> bool; acknowledge(key: str, *, message_ids: Sequence[str]) -> None; resolve(key: str, *, outcome: Literal['sent','not_sent'], evidence: str) -> None; outcome(key: str) -> str. Transaction states sending/confirmed/unknown/not_sent. Add owner CLI resolve command requiring evidence. Sending at restart is treated as unknown.

- [ ] Test intent durable before sender, concurrent exact retry sends once, crash after send blocks retry, confirmed success skips, explicit not_sent permits retry, changed content gets distinct identity, and partial text/image/target routes preserve confirmed sends.
- [ ] Run uv run pytest tests/a_share_daily/test_delivery_intents.py tests/a_share_daily/test_delivery_idempotency.py -q; confirm unmet persistence behavior fails.
- [ ] Wrap actual per-route/target Lark text/image, webhook and Hermes sends; preserve/import successful v1 receipt confirmation. Use provider-supported lookup/idempotency only where actually implemented; otherwise require explicit resolution. Store no raw recipient identities in public evidence.
- [ ] Pass new tests and all existing receipt/routes/sender tests; test CLI help and fake-send resolve/retry example.
- [ ] Commit: feat: persist delivery intents and unknown outcomes.

### Task 3: Business-result recovery smoke

**Files:** quant-intel-platform: create tests/test_assurance_recovery_smoke.py and docs/operations/recovery-assurance.md; extend tests/test_business_freshness.py; modify src/ops_common/recovery_state.py and market_intel_recovery.py only to surface new outcome evidence.

**Interfaces:** Task 2 delivery outcome plus existing FreshnessResult; report expected/actual date, complete artifact inventory, delivery outcome and recovery outcome.

- [ ] Test stale upstream, corrupted receipt, restart during recovery, fake owner-CLI/artifact-to-report full flow and partial-route recovery without duplicated confirmation.
- [ ] Run uv run pytest tests/test_assurance_recovery_smoke.py tests/test_business_freshness.py tests/test_recovery_modules.py -q; confirm new outcome assertions fail where absent.
- [ ] Exercise actual local orchestration with fake external endpoints and temporary assets; surface unknown status instead of success. Document diagnosis/resolution with verified command help.
- [ ] Pass full owner-local project_tools/check_all.py --scope all and required CI. No deploy/config changes in this task.
- [ ] Commit: test: verify business results after recovery faults.
