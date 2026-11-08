# Recoverable minute execution sessions

`quant_platform.backtest.minute_session.MinuteSession` reuses the existing minute
matcher and economic ledger. It adds event stepping, source-bound JSON checkpoints
and a conservative delayed view of financial account snapshots.

Construct with the same targets, bars and `MinuteExecutionConfig` as the minute
simulator, plus a callable policy implementing `checkpoint()`. Use `step()` to
advance one existing event, `checkpoint()` before finalization, and `run()` to
finish. Restore with `MinuteSession.restore(targets, bars, config, checkpoint,
policy=restored_policy)`. The caller reconstructs its policy from the checkpoint's
`policy` field; the session verifies canonical state and policy implementation
identity. Policy source files must be inspectable. Only the exact `LinearImpact`
class, or no impact, is supported for recoverable impact state.

Financial snapshots deliver after `report_delay_seconds`; raw market marks remain
independent historical observations. While any financial report is undelivered,
new target submissions are suppressed at both decision and entry. Policies still
receive observations, including an explicit pending-report marker. This is a
conservative waiting protocol, not a model of informed trading under partial state.
Exchange cancellation is synchronous; its acknowledgement is delayed. No network
cancel latency, queue position or endogenous market response is simulated.

Checkpoint state includes T+1 inventory, parent commissions, orders, fills, pending
references, policy snapshots, impact and delivery queue. Inputs, configuration and
loaded implementations are content-bound. Digests detect accidental modification,
not a hostile party able to rewrite a checkpoint. Nonfinite valuation diagnostics
retain explicit tagged encodings; they are not silently repaired. Restoring requires
the same sources and inputs. Finalized sessions cannot be checkpointed or rerun.

This initial session API does not accept corporate actions or valuation events.
It therefore cannot certify a historical strategy requiring those events. Existing
synchronous execution remains available for that separate scope. Result summary
fields state delivery, cancellation and remaining report semantics. Zero-delay
parity covers financial tables; delivery metadata intentionally differs.

Pass `quantity_locks=(QuantityLock(...),)` using
`quant_platform.backtest.quantity_locks.QuantityLock` for share-preserving
restrictions. Each immutable notice supplies `available_ns`, `start_ns`, `end_ns`
(integer UTC nanoseconds), a tuple of unique `symbols`, and `source_binding`.
The effective interval is inclusive and begins after both availability and start.
The owner cancels only remaining orders for those symbols, skips their target
sizing and prohibits fills; holdings and cash are never overwritten. Other
symbols can trade subject to the existing account and report guards. Cancellation
acknowledgements use the ordinary delayed financial snapshot queue. Release never
revives cancelled orders. A bar overlapping the interval is entirely unavailable
for that symbol because an intra-bar unlocked execution time is unknown.

Policy state exposes `locked_symbols` at the current event and `quantity_locks`
whose availability clocks have arrived, including received future restrictions.
Neither is a certification of historical notice provenance. Notices, boundaries
and active guards are checkpoint-bound. Old checkpoints require their original
pinned sources; this change does not migrate them. No notices preserves existing
financial behavior, including empty sessions. Corporate actions remain outside
this API, so share conservation here concerns trading only.
