# Qlib expression preflight implementation plan

Goal: reuse upstream operators behind a finite deterministic research boundary.
Spec: ../specs/2026-11-28-qlib-preflight-design.md

## Task 1: Real Qlib admission adapter
- [ ] Write tests for window metadata, future roles, unknown fields, unsafe syntax,
      bounded windows, optional dependencies and context identity; observe RED.
- [ ] Implement packages/alpha/src/alpha_research/qlib_preflight.py with lazy
      upstream imports and no expression eval; observe GREEN with locked Qlib.
- [ ] Run native/research backend regression and static checks.

## Task 2: Adoption guidance and review
- [ ] Document reuse vs replacement and exact Qlib runtime support limits, with
      English default and Chinese companion. Do not claim full backend support.
- [ ] Independently review, fix reproducible findings and validate current main.
- [ ] Commit, push, create/merge owner PR and close only task-owned resources.
