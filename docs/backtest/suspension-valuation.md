# Explicit suspension valuation

Language: English · [简体中文](suspension-valuation.zh-CN.md)

The daily adapter preserves Core's opt-in valuation policy. The default still requires a current quote for complete valuation evidence. A carried mark never becomes an executable quote.

For adjusted-price sequenced NAV without corporate-action events, callers may declare `valuation_policy="suspended_last_quote"`, a separate `valuation_suspension_col`, and a positive `valuation_max_stale_sessions`. Core qualifies a missing current mark only from an explicit boolean suspension witness, a matching live-owner prior quote and the stated session-age limit. Unknown witnesses or marks remain incomplete. Tradability, limit, price and liquidity selectors cannot double as suspension evidence.

Pass the Core `ExecutionSimConfig` to `quant_platform.backtest.engine_daily.build_daily_request` with `price_basis="adjusted"`. The adapter retains the config and delegates all financial state and policy validation to Core. It does not fill missing executable prices, reconstruct a cash ledger or approve a valuation assumption for a particular investment product.

Read `valuation_marks.current_marks` and `missing_symbols` separately from `policy_valued_symbols`, `policy_quote_dates`, `policy_quote_ages` and `unresolved_symbols`. `endpoint_complete` means complete under the declared policy. Native and normalized summaries identify the applied policy and the number of policy-valued endpoints; this must not be described as all-current pricing.

Raw-share, corporate-action, ideal and capacity opt-in requests are unsupported and rejected. Last quotes may differ from realizable value. The policy does not establish vendor authenticity, publication-time availability, delisting recovery value or market execution quality. Keep source and timing evidence with the caller's published result.

Core owns the detailed [input and valuation contract](https://github.com/runchengxie/quant-backtest-engine/blob/main/docs/product/daily-inputs.md). Historical migration receipts and previously pinned runs retain their original provider environment.
