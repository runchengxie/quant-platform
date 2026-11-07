# Backtest research mechanisms

Extend the existing reference APIs with explicit admission contracts, deterministic
joint stress, composite account/impact checkpoints, scoped cost calibration and a
small convex multi-period optimizer. Reuse event-account economic and delivery
state; do not implement another matcher or claim new Rust capabilities.

Admission separates hard temporal/semantic violations from unknown provenance.
Mechanism experiments can preserve unknown evidence; formal use must reject it.
Joint stress is non-mutating, event-keyed and respects supplied price limits.
Composite recovery binds input/source identity and exact cursor to owner account
and impact state. Cost fits use only completed training observations and retain
signed residuals, domain, grouping and evidence kind. Multi-period planning is
long-only with cash, PSD risk, explicit turnover costs and per-step trade bounds.
Only its first decision is executable; the caller replans from actual state.

Synthetic fixtures prove mechanics. Historical validity, broker calibration,
market-response identification and production promotion remain separate evidence.
