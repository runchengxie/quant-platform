# Explicit nontrading valuation events

**Goal:** Separate declared nontrading valuations from executable bars without changing cash, legal holdings or default missing-mark rejection.

**Architecture:** A timezone-aware valuation event establishes a nontrading state and a per-share mark at its effective time. Later valuation events may change that mark but never make the instrument tradable. Apply events before sizing and at their own timeline instants. Retain event provenance, source time and a valuation ledger. Research assembles declared impairment/observed-price policies outside the provider and reruns funded pilots in fresh external directories.

**Authorization:** The user requested implementation exploration after the four-step recommendation: independent valuation events; CNY 1m/10m full impairment pilots; separately qualified quote scenario; disposal only after separate rules. No actual disposal is in this scope.

**Constraints:** No vendor records in provider; preserve defaults, corporate entitlements, quantity, cash and old studies. Reject duplicate/invalid events and conflicting executable bars. Mark source times remain inspectable; no future price backfill. Zero marks cannot cause division by zero for positive targets. Event-based nontrading eligibility cancels affected orders and blocks new trading. A recognized persistent event mark is explicitly an assumption, not an observed daily quote.

- [x] Add synthetic red tests for zero/nonzero valuation, causal event timing, persistent explicit marks, unaffected missing marks, no cash/share mutations, no affected fills, positive target guard, receivables, duplicate/invalid/conflicting inputs.
- [x] Implement event contract, lifecycle, valuation ledger and provenance; keep no-event behavior unchanged.
- [ ] Validate full provider suite and lint; independently review, PR and merge provider before pinning consumer.
- [ ] Add source-bound research policy assembly, receipt/fingerprint/CLI support and regression tests; default unchanged and scenarios labeled.
- [ ] Freshly rerun two capital pilots under explicit full impairment; independently reconstruct all ledgers. Observe-price scenario remains qualified by single-source evidence and gap rules.
- [ ] Record reviewed outcomes/limitations, validate and merge consumer; keep incomplete matrices nonpublic and preserve original 18 results.

Provider verification: 1749 passed, 13 skipped; Ruff lint/format and strict typing pass. Independent review reproduced and fixed a mixed-timezone calendar bug; UTC and market-local equivalent instants now preserve prior-day NAV and record-date entitlements. Consumer tests and real source-packet validation remain separately scoped.
