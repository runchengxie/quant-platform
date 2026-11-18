# Canonical Model Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Work task by task with one product implementer at a time, independent task reviews and a whole-provider review. The owner has requested implementation; preserve standing integration authorization.

**Goal:** Converge the public model and event-stream implementation in quant-deep-learning without losing either owner's supported behavior.
**Architecture:** Publish the canonical model provider first, independently of Platform. Keep Engine financial simulation in its existing extraction plan. Simulator shims, private CLI migration and Platform file removal are later dependency-gated cuts; this provider plan does not pretend to complete them.
**Tech Stack:** Existing Python/PyTorch/NumPy/Polars, setuptools wheels, locked uv tools, synthetic regression fixtures.
**Spec:** [English package ownership design](../specs/2026-11-09-package-ownership-design.md) and [中文设计](../specs/2026-11-09-package-ownership-design.zh-CN.md).

## Global Constraints

- Deep Learning is the canonical training owner.
- Do not blindly replace current code with an older copy.
- Preserve current canonical model work and any useful Platform-only changes through reviewed owner changes.
- No real training or new empirical result is needed for an ownership move.
- Keep training dependencies out of Engine/base Platform imports.
- Never install two wheels that overwrite the same module or CLI.
- Existing results/checkpoints retain the actual original producer/source/dependency identity.
- Equal schema strings do not establish restore compatibility.
- Every transfer preserves original license/copyright and per-file provenance, including model/coordination code moving into owners with a different default license.
- Code, acceptance tests, paired EN/ZH installation/API/capability guides, source history links and migration maps move together.
- Do not label future provider/compatibility work as installed, released or deployed.

## Review Focus

1. A same-named module differs in substantive behavior, not only formatting: retain canonical additions and prove the supported Platform behavior (Tasks 1–3).
2. A split class or helper changes import/checkpoint identity: test aliases and state-schema conflicts, retain full pinned historical route (Tasks 2–4).
3. Python 3.12 typing syntax breaks the declared Python 3.10 boundary: use compatible typing and run actual installed 3.10 checks (Tasks 2–4).
4. An owner feature disappears when a smaller Platform loader replaces a full builder: retain materialization/overlay construction and validation APIs together (Tasks 1–3).
5. A standalone provider passes while the old combined installation overwrites files/commands: audit wheel ownership and explicitly reject that installation profile (Task 4).

## Source and gates

D means quant-deep-learning. P means quant-platform. Re-fetch their actual owner remotes and use a new D worktree before implementation. Read D/AGENTS.md, README and docs/documentation-index.md. Initial clean source references are D d368fe6791fadbebab1c8fb90a851cc99a84ab4a and P 7a618bddd8fdeee5dbe37fe5b54a9698e0de5355; preserve immutable reference checkouts and DATA evidence. If either advances, refresh the catalog and assess differences before using it as an oracle.

The model-only closure is 26 P files, excluding all nine ticknet/simulator files already assigned to Engine. Two common files are byte-identical, fifteen common files have different ASTs, and nine P modules are absent at D. This is a source inventory, not behavioral equivalence.

Absent D modules to account for: eventstream/checkpoints.py, cli.py, daily.py, data_loading.py, evaluation.py, materialized_cli.py, materialized_schema.py, training.py and training_config.py. Common divergent modules: dataset.py, model.py, train.py; eventstream/__init__.py, benchmark.py, dataset.py, fingerprint.py, gradient_audit.py, input_profile.py, materialized.py, model.py, pack.py, storage_readiness.py, target_overlay.py and train.py.

D's materialization and overlay builder APIs must remain available; P's smaller target_overlay loader is not a replacement for D's full builder. Type-only casts/override decorators are not evidence of a different model, but runtime protocol or numerical changes require explicit oracle coverage.

Version 0.2.0 becomes 0.3.0 for this provider. No PyPI publication is needed; actual merged VCS revisions and wheel hashes are release identities. If the inspected current release has advanced beyond this baseline, record a minor-version adjustment before source changes instead of overwriting an existing release identity.

Use external owner DATA environments/builds/receipts; no real market data, checkpoints, GPU training, production settings, scheduler changes or historical trial updates. Full required D checks include Python hygiene/Ruff/format/ty/notebook/code-quality/pytest warnings-as-errors/coverage/synthetic smoke/compilation and existing web tests/build. Follow the actual AGENTS commands and locked dependencies. Add relevant actual Python 3.10 installed checks. Do not modify shared hooks or weaken budgets.

## Task 1: Freeze the public module and behavior catalog

**Files:** Create D/docs/migration/model-owner-catalog.json, D/project_tools/check_model_owner_catalog.py and D/tests/test_model_owner_catalog.py; add D/docs/migration/model-provider{,.zh-CN}.md.

**Interfaces:** Catalog schema ticknet.model_owner_catalog.v1 contains actual source repository/revision/path/hash, destination module, public symbols, disposition (identical/typing-only/refactored/behavior-difference/new-owner-module), supported contract/checkpoint scope, oracle test names and original license. It contains public paths only. The checker validates inventory completeness, exact frozen source links, unique destination file ownership and no simulator/native financial file in the model cohort. Runtime results/golden traces remain in external DATA; source keeps only synthetic fixture inputs and expected literal contracts.

- [ ] Add RED coverage for missing model files, accidentally included simulator files, duplicate physical destinations and omitted owner-only public APIs. Assert all 26 source modules are accounted for and each behavior-difference row names an executable oracle.
- [ ] Classify each common divergence using signatures, definitions, calls and original tests. Distinguish P split refactors from missing D features; do not infer behavior from AST equality alone.
- [ ] Capture deterministic synthetic old-P and canonical-D model/data/protocol outputs in separate installed reference environments, including malformed inputs, label/window boundaries, checkpoint configuration and materialization/overlay validation. Record source/dependency identities with those outputs.
- [ ] Write the real per-module dispositions and EN/ZH scope, including unsupported historical restore routes. Run catalog tests/checker and affected owner document tests; commit and review before implementation depends on the map.

## Task 2: Converge model, dataset and artifact contracts

**Files:** Modify D/src/ticknet/{dataset,model,train}.py and D/src/ticknet/eventstream/{dataset,model,fingerprint,materialized,target_overlay,storage_readiness}.py; create D/src/ticknet/eventstream/{materialized_schema,data_loading}.py only for the reviewed split closures. Port relevant assertions from P/tests/microstructure/test_{eventstream,eventstream_model,materialized_contract,materialized_schema,target_overlay}.py into focused D tests without duplicating financial simulator tests. Update the paired migration/API guides.

**Interfaces:** Preserve the cataloged public signatures and actual model/config/artifact schemas. Existing D construction APIs and Platform-only validation behavior coexist in the canonical owner; shared class exports refer to one class object. No new loss function, feature scaling, label alignment, weight shape, rounding or artifact hash semantics is introduced by extraction.

- [ ] RED regressions assert the missing cataloged P behavior and preservation of D-only builders, malformed artifact rejection, cross-file/window/label discipline and unsupported checkpoint/config rejection.
- [ ] Port complete helper closures while preserving canonical additions. Replace Python-3.12-only annotations/decorators with Python-3.10-compatible equivalents without changing execution.
- [ ] Run synthetic forward/state-dict roundtrips using fixed tensors/weights and full artifact validation comparisons against the declared reference. A difference must be explained in the catalog before it can become a new expected value.
- [ ] Run focused owner tests on actual Python 3.10 and current supported CI interpreter; retain logs and byte/source identities externally. Commit and independent review.

## Task 3: Converge training/evaluation orchestration inside the model owner

**Files:** Modify D/src/ticknet/eventstream/{train,benchmark,gradient_audit,input_profile,pack,__init__}.py; add the cataloged D/src/ticknet/eventstream/{checkpoints,cli,daily,evaluation,materialized_cli,training,training_config}.py closures. Port relevant P test_eventstream_{daily,training}.py assertions and preserve D/tests/test_eventstream_{train,benchmark,benchmark_sweep,gradient_audit,input_profile,pilot,vq_warmstart}.py. Update paired public command/API guides.

**Interfaces:** Existing canonical model CLI names remain D-owned. Splitting a monolith preserves its public imports, default arguments, synthetic forward/training-smoke behavior, exact resume-position/config guards and artifact protocols. Model-owner training helpers are distinct from strategy selection/promotion in private Research and from workers in Runtime.

- [ ] RED tests cover the missing split imports, legacy/canonical class identity, configuration conflict, resume-position and fixed-window selection failures, plus current canonical CLI help/option compatibility.
- [ ] Extract or merge the cataloged closures without removing D's current builder/benchmark/gradient functionality. Preserve public import aliases and source-bound historical recovery limits; no cross-owner source imports.
- [ ] Run all affected synthetic model tests and genuine CLI --help commands; compare documented names/options. Do not run real-data training.
- [ ] Run D required gates and the actual relevant Python 3.10 profile; commit with paired documentation and independent review.

## Task 4: Publish and verify the standalone model provider

**Files:** Modify D/pyproject.toml, uv.lock, source-specific license/notice packaging and migration catalog/docs; create D/project_tools/verify_installed_model_owner.py and D/tests/test_installed_model_owner.py. Update README/documentation index and existing wheel configuration only as required.

**Interfaces:** Installed quant-deep-learning 0.3.0 owns ticknet model/dataset/eventstream files. Verification consumes explicit wheel paths and expected source revision, runs outside source using -I, requires module origins inside the environment and rejects duplicate RECORD paths/console entry points in the supplied profile. Historical checkpoints keep their original full provider/dependency environment. Current canonical model output identities name the actual implementation revision, never a fabricated original producer.

- [ ] RED installed-profile tests reject editable/source imports, duplicate ticknet owners, duplicate canonical CLI writers, missing license terms and unsupported checkpoint lineage.
- [ ] Build actual wheels with original per-file source/license notices. Install canonical D alone in fresh Python 3.10/current environments and exercise model, data, artifact and command contracts without Platform/Runtime/Research/Engine.
- [ ] Compare wheel RECORD and entry points against the inventoried legacy P wheel: document the old combined profile as conflicting rather than installing over it. This provider release does not remove P files or claim the combined cutover is complete.
- [ ] Run current combined D gates, whole-provider review, PR checks and merge. Rebuild/install the actual merged revision and record source/wheel/CLI ownership receipts. Verify any task-related existing docs/site deployment; clean only this task's merged resources.

## Subsequent dependency gates

Remaining package cleanup is still authorized and tracked separately. Engine provider B and its Platform consumer must merge before owner-side ticknet.simulator shims switch to quant_backtest_core. Private Research must rename duplicate customized model commands or retain explicit pinned legacy profiles before a combined D/Research installation claims unique CLI ownership. Platform must stop shipping its ticknet implementation only after these providers and supported consumers are verified, coordinated with the existing Engine consumer cohorts. Generic strategy coordination and generic OMS extraction have separate owner plans; this model plan does not copy their implementation or publish private source paths.

## Controller self-review

All model-specific design requirements map to Tasks 1–4; later simulator/CLI/Platform removals remain explicit dependency gates, not released claims. Task 1 makes every divergent module's chosen behavior and executable oracle a reviewed input to Tasks 2–3. Python 3.10, source/checkpoint identity, owner-only API preservation, wheel collision and licensing each have explicit tests. No financial arithmetic, production state or real research evidence is changed by this plan.
