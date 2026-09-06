# 因子归因实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**目标：**增加主动收益和主动风险分解，后续消费平台风险模型并发布归因证据。

**规范：**`docs/superpowers/specs/2026-09-02-factor-attribution-design.md`

- [x] Add tests for return reconciliation, risk reconciliation, and asset/factor mismatch.
- [ ] Run focused tests and confirm RED before implementation.
- [x] Implement factor return contribution, specific residual, cost drag, factor variance contribution, and specific variance contribution.
- [x] Document why Brinson attribution remains a separate semantic layer.
- [ ] Run `uv run --extra dev pytest tests/test_factor_attribution.py -q`.
- [ ] Run repository lint, format, typecheck, full test, and maintainability gates.
