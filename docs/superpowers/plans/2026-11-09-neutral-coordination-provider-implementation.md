# Neutral Coordination Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development, one product implementer at a time, independent task reviews and a whole-provider review. Implementation was requested; preserve existing integration authorization.

**Goal:** Publish the genuinely neutral owner-control API from quant-task-orchestrator without importing research stages or bypassing durable workflow approval.
**Architecture:** Add an independent stdlib-only canonical namespace inside the existing coordinator. Preserve the exact neutral contracts/delegation semantics. Legacy namespace files and research-specific helpers stay on their recorded owner until a separate compatible consumer cut.
**Tech Stack:** Python 3.12+, existing hatch wheel, stdlib dataclasses/protocols, unittest, existing coordinator CI.
**Spec:** [English package design](../specs/2026-11-09-package-ownership-design.md) · [中文设计](../specs/2026-11-09-package-ownership-design.zh-CN.md).

## Global Constraints

- Cross-owner DAG, plan approval, audit and coordination belong to quant-task-orchestrator.
- Research owns admission, economic evidence and promotion.
- Never import private research source, copy strategy configuration, or change production schedules to test an adapter.
- A stateless compatibility helper is not an implicit approval to start a durable research workflow.
- Each physical file has one wheel owner.
- Every transfer preserves original license/copyright and per-file provenance, including model/coordination code moving into owners with a different default license.
- Public examples are synthetic.
- Keep aliases for at least two minor cycles and until all recorded supported consumers migrate or have an explicit pinned legacy environment.
- No broker access, order submission, production switch, real training or data acquisition is authorized by this code migration.

## Review Focus

1. A neutral artifact receipt is mistaken for durable workflow approval: existing approval/store/audit rules remain enforced (Task 1).
2. A public class becomes incompatible when old/new packages are mixed: document identity boundaries and test one canonical class per supported profile (Tasks 1–2).
3. A research-specific helper enters the generic coordinator because of its docstring: exclude training ports, OutputContext overrides, AFML release policy and CN gross-exposure rules (Task 1).
4. The coordinator's MIT metadata erases Apache terms of moved files: ship original source-specific notices in the wheel (Task 2).
5. Canonical provider installation silently overwrites old strategy_pipeline files: this provider owns only quant_task_orchestrator files; compatibility is later and opt-in (Task 2).

## Frozen scope and rollout

O=quant-task-orchestrator, P=quant-platform. Refresh actual owner heads and create an isolated O worktree before code. Reference P source7a618bddd8fdeee5dbe37fe5b54a9698e0de5355; O initial source3db947 prefix must be resolved/recorded in full before dispatch. Preserve reference environments. O0.7.0 becomes0.8.0 unless current merged release has advanced; record any necessary minor adjustment before implementation.

Only P strategy_pipeline/control_plane/{contracts,currentness,runner,publication,handoff}.py and the neutral subset of ports.py move into this provider. Existing contracts' fields/signatures/validation/hash meanings stay unchanged. Neutral ports are RunOwner.run(RunRequest)->ArtifactRef, ArtifactPublisher.publish(PublicationRequest)->ArtifactRef, HandoffPublisher.publish(HandoffRequest)->ArtifactRef and ArtifactWriter.

The current ports.py also has domain-specific training hooks/adapters. OutputContext hardcodes research stage keys/overrides; AFML lineage attaches named research receipts; targets export hardcodes CN gross exposure0.99. These are excluded from O canonical code. Their final Research/public-legacy routes must be planned separately before Platform stops shipping them; no public-to-private import is permitted as a shortcut.

## Task 1: Canonical stateless owner control

**Files:** Create O/src/quant_task_orchestrator/owner_control/{__init__,contracts,ports,currentness,runner,publication,handoff}.py, O/tests/test_owner_control.py and paired O/docs/owner-control{,.zh-CN}.md. Preserve existing O contracts/api/store/approval implementations.

**Interfaces:** Re-export the original neutral ArtifactRef, RunRequest, RunReceipt, PublicationRequest, HandoffRequest; three protocols, writer callable, currentness policy/result/type and evaluate_input_currentness; run(request,*,owner,publisher)->RunReceipt, publish_artifact(request,writer)->ArtifactRef and publish_handoff(request,publisher)->ArtifactRef. These live in the new owner_control namespace and do not mint durable authorization.

- [ ] RED tests cover successful exact receipts, owner exception, missing/failing publisher, wrong returned artifact types, stale-production/research currentness variants and original policy IDs.
- [ ] Preserve public neutral source bodies except namespace/import changes. Split ports at the neutral symbol boundary, with no training dependencies or research configuration.
- [ ] Add a synthetic counterexample where a stateless receipt is offered as approval to existing durable dispatch; prove it does not authorize a store transition, bypass plan-hash confirmation or remove audit records.
- [ ] Compare complete old/new synthetic receipt/currentness payloads and failures in separate installed profiles. Document old/new class identity boundaries until aliases actually switch.
- [ ] Run focused new tests plus affected approval/audit tests and full required O unittest/compile/diff gates. Commit with paired guides and independent task review.

## Task 2: Installed provider and source-specific provenance

**Files:** Update O/pyproject.toml and packaged NOTICE/license records, README/docs navigation; add O/project_tools/verify_installed_owner_control.py, O/tests/test_owner_control_installation.py and a public source inventory under docs/migration/.

**Interfaces:** Standalone O0.8.0 wheel remains stdlib-only; canonical imports require no Platform, Engine, Runtime or private Research. The current quant-task command retains behavior. No new training CLI or strategy_pipeline namespace is shipped by the default wheel.

- [ ] RED installed tests reject editable/source-tree imports, reverse owner dependencies, old namespace file/console overwrites and missing original Apache source terms.
- [ ] Build a real wheel, install outside source in fresh supported interpreters and run the neutral contracts/receipts plus existing coordinator tests. Audit RECORD paths/entry points against the pinned legacy P wheel.
- [ ] Preserve Apache provenance for moved source alongside the existing project's actual license metadata; do not claim relicensing.
- [ ] Run current full O checks including existing frontend syntax/browser smoke where required by AGENTS, whole-provider review, PR checks and merge; verify the actual merged wheel/API and task-related existing deployment, then task-only cleanup.

## Subsequent compatibility gate

An optional strategy_pipeline compatibility distribution must be designed alongside the private Research consumer and pruned Platform wheel. The root/control_plane files, training child modules and console command each need one physical owner. Research-specific public historical APIs must retain an explicit supported legacy route and their actual environment; do not silently import private Research from O or remove aliases early. This neutral provider can merge independently and does not certify the later combined installation.

## Self-review

Both tasks deliver independently testable neutral mechanisms and their installed proof. Each of the five review inputs has explicit coverage. The source-specific research helpers are explicitly excluded rather than misclassified by their module titles. Consumer/compatibility work remains active and provider-first.
