# Modeled USD Execution Reference Evidence

Date: 2026-10-05  
Status: Draft for review  
Owner: `portfolio_backtester` in `quant-platform`.

## Purpose

Let research callers replay transactions against an explicit modeled price reference when source data does not establish an execution-eligible market mark. Preserve the distinction between modeled research transactions and verified execution evidence.

## Design

- Keep `USDPriceObservation.execution_eligible` and `select_usd_price(..., execution=True)` strict and unchanged. A modeled reference can never satisfy that selector.
- Add a separate immutable `USDModeledExecutionPrice` record with instrument ID, local session date, caller-derived scheduled UTC open, positive local-currency reference price, unit, source `ArtifactRef`, session-policy ID and nonblank model ID. The type does not expose an eligibility flag.
- Add opt-in request/config fields. Existing callers default to the verified-only path. Modeled execution selection requires an exact instrument and scheduled-time match; it never uses an as-of match, stale mark or fallback close.
- Preserve the modeled evidence kind, source lineage, model ID, session date and assumed timestamp in transaction and bundle outputs. Modeled references remain noneligible, produce no broker orders/fills, and retain `orders_submitted=false`.
- Permit `assumed_market_session` FX observations only when assumed availability and modeled execution are both explicitly enabled. Verified executions continue rejecting assumed FX.
- Reuse existing USD cash accounting, deterministic same-time sell-before-buy ordering, affordability scaling, commission, slippage and FX cost calculations. Do not add strategy, exchange-calendar, provider, credential or data-specific behavior to the public platform.

## Validation requirements

- Missing, duplicated, mismatched, invalid or unapproved modeled references fail closed.
- The replay and publisher reconcile NAV, cash, quantity, costs and source lineage independently.
- A corrupted modeled price source, session, model ID, or assumed FX basis fails bundle validation.
- Existing verified-only replay and bundle behavior remains unchanged when the new options are omitted.
- Synthetic fixtures prove the distinction; no real data or strategy parameters enter this repository.

## Deferred scope

Exchange-session calculation, data availability inference, market-specific model selection, broker order handling, settlement dates, foreign-currency cash, dividends, corporate actions and futures remain caller-owned or require separate capabilities.

## 中文摘要

本设计为公共 USD 账本增加显式选择的模拟参考价输入，同时保持原有可验证执行行情校验严格不变。模拟价单独保留来源、交易日、假设时间和模型 ID，只生成研究诊断交易，不得进入券商订单或成交记录。交易日历、市场数据时钟及策略规则仍由调用方负责。
