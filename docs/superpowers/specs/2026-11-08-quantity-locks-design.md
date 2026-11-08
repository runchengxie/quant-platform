# Scheduled share-preserving execution locks

A minute session must preserve physical holdings of restricted securities while
allowing other securities to trade. A frozen target weight cannot do this when
NAV, marks or lot rounding change between decision and entry.

Add immutable `QuantityLock` notices with integer UTC availability, inclusive
start/end clocks, nonempty unique symbols and a provenance identifier. A notice
acts only after both receipt and effective start. Its end does not recreate
cancelled orders. The owner cancels active orders of locked symbols and skips
new sizing and fills for them. No target quantity, cash or holding is rewritten.
Policy state exposes active symbols; delayed financial acknowledgements retain
the existing conservative whole-account report guard. Overlapping notices use
the union. Locks and their event boundaries survive exact checkpoint recovery.

Approaches considered: the current whole-account pause is conservative but
prevents unrelated trading; translating current quantities into weights changes
shares after repricing; owner-side execution locks preserve shares directly.
The third approach is the implementation choice under the user's instruction to
advance all proposed work. This is a deterministic research mechanism, not a
broker connection, historical notice certification or a corporate-action API.
Existing sessions without notices retain their financial behavior. Old source
checkpoints still require their original pinned implementation.
