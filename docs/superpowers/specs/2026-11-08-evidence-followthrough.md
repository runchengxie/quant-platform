# Recoverable minute execution design

Add a strategy-independent event session over the existing minute matcher, with
zero-delay financial-table parity, delayed account snapshots and JSON recovery.
Use the existing matching/accounting implementation instead of a second matcher.

Policy decisions use delivered cash/inventory, fresh independent raw quotes, and
read-only pending orders. Any hidden financial report blocks new submissions at
both decision and entry. Exchange cancellation remains synchronous, with delayed
acknowledgement; queue position and network cancellation latency are not modeled.

Bind input bytes, configuration, policy implementation and loaded financial source.
Restore all mutable owner state, including T+1 inventory, commission accumulation,
orders, fills, policy state, impact and delivery. Only exact LinearImpact or no
impact is recoverable. Reject changed inputs, code, policy and tampered checkpoints.
Corporate actions and valuation events remain outside this initial API.
