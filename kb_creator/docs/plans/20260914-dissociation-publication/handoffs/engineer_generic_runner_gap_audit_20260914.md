# Engineering handoff receipt — generic runner gap audit

- Goal id: `20260914-dissociation-publication`
- Step id: `3-generic-runner-gap-audit`
- Role: engineering
- Requested model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable (role assignment is policy, not platform proof)
- Timestamp: 2026-09-14T02:59:36+03:00
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`
- Scoped override: none
- Scope: read-only audit of the reusable source-reconstruction core and the minimum scenario-neutral control-plane addition required for a third contract-defined scenario. No code, contracts, canonical plan/context/status, generated artifacts, Git, acceptance, or release state changed.

## Result

The five reconstruction primitives already exist and are largely scenario-neutral:

1. `prepare_mineru_three_view_inputs.py` seals an input hash, ordered one-based page mapping, deterministic vector/raster inputs, and bounded resume identity.
2. `run_mineru_three_view.ps1` provides two fixed MinerU profiles with controlled runtime environment.
3. `compare_mineru_three_views.py` normalizes all three views, retains conflicts/assets, and emits comparison JSON/Markdown.
4. `audit_mineru_ai_merge_fidelity.py` is a fail-closed decision-vs-packet audit with an exact reviewed allowlist.
5. `materialize_mineru_ai_merge.py` requires exact decision coverage, preserves decision bytes/provenance, rejects unsafe assets, and atomically materializes a candidate.

They cannot yet be invoked as a declarative third-scenario flow. Each needs independently supplied paths/options; no runner consumes `scenario_contract.v1`, seals one run, invokes the fixed graph, records a common stage state, or turns comparison conflicts into a typed review queue. The current contract is an intake validator, not a runnable `RunSpec`: it has no run root/tool resolution/three-view options/decision input declarations. This is the precise generic gap; a new scenario-named wrapper would reproduce the problem.

There are also two bounded reusable-core issues to isolate while adapting the runner, rather than encode in a Dissociation exception:

- the preparer rejects any source page not exactly US Letter and rasterizes to Letter (`LETTER`); page geometry must be per-page source geometry or a declared generic rendering policy;
- `finalize_mineru_reconstruction.py` hard-codes Viral's 39 handout labels and therefore is not in the third-scenario reconstruction core. It must remain outside Wave 0, or later read required handouts from the contract instead of a constant.

## Minimal implementation boundary (Wave 0)

Implement only a generic reconstruction control plane; do not reach MASTER_EN/RU, assets finalization, HTML/PDF, package freezing, or conversion of existing reference builders.

Proposed package/files:

- add `kb_creator/pipeline/core/{identity,jsonio,paths,inventory,process}.py`: shared canonical JSON, SHA-256 records, safe relative paths, deterministic inventories, atomic directories, subprocess capture, and typed errors;
- add `kb_creator/pipeline/{models,manifests,reconstruction}.py` plus `kb_creator/__main__.py`: public `doctor`, `preflight`, `run`, and `resume` commands, initially exposing target `reconstructed_en` only;
- add versioned schemas under `kb_creator/contracts/`: `run_spec.v1.schema.json`, `stage_manifest.v1.schema.json`, and `review_queue.v1.schema.json`; keep `scenario_contract.v1` unchanged in this first slice unless the architect separately accepts a compatible extension;
- add `kb_creator/tests/support/` synthetic PDF/MinerU-tree fixtures and focused `test_pipeline_core.py`, `test_reconstruction_runner.py`, `test_stage_manifest.py`, and `test_review_queue.py`.

The runner may call the existing five scripts as adapters without changing their current CLI/output schemas. It owns only path derivation, source/contract validation, stage boundaries, process capture, manifests, and resume validation. The three MinerU invocations should be represented as one `mineru_three_view` stage with the three exact child outputs declared in its manifest; comparison is the next stage. Human merge decisions remain external inputs, never generated or auto-approved by the runner.

### Public CLI contract

```powershell
python -m kb_creator doctor --json
python -m kb_creator preflight --contract <contract.json> --source <source.pdf> --run-root <empty-run-root> --target reconstructed_en --json
python -m kb_creator run --contract <contract.json> --source <source.pdf> --run-root <run-root> --target reconstructed_en --mineru-root <mineru-root> --json
python -m kb_creator resume --run-root <run-root> --target reconstructed_en --decisions <DecisionManifest.json> --json
```

`preflight` is non-mutating. `run` creates an empty, identity-bound run root and stops with exit code for `needs_review` after comparison/review-queue emission. `resume` first revalidates the complete `RunSpec`, prior stage manifests, source/contract/code/tool identities, and supplied decision-manifest hashes; it only materializes after every queue item is closed. No command accepts shell fragments, Python import paths, or scenario-specific executable names.

### Stage and queue behavior

`run.json` (`RunSpec.v1`) binds canonical contract bytes/hash, source byte/hash/page geometry identity, requested target/profile, resolved tool versions/paths, implementation identity, run/cache roots, and any external decision manifest identity.

Each stage writes `stages/<ordinal>-<name>/stage.json` (`StageManifest.v1`) with: schema, stage name/version, state (`pending`, `running`, `blocked`, `needs_review`, `failed`, `succeeded`, `cached`), ordered input identities, options, tool/implementation identities, output inventory/hash, evidence paths, upstream manifest hashes, cache key, timestamps, and structured diagnostics. Cache/resume is valid only when every identity and declared output inventory matches; otherwise rerun from the earliest stale stage. This wraps existing local `sample_pages.json`, comparison JSON, audit JSON, and merge provenance rather than replacing them.

Comparison creates `review_queue.json` (`ReviewQueue.v1`), one deterministic item per source page plus an item for each semantic conflict/asset ambiguity. Every item binds source page, comparison/packet hashes, allowed decision schema/path, category, and state. States are `open`, `blocked`, `decided`, and `invalidated`; an item becomes `decided` only through a hash-bound `DecisionManifest.v1` supplied to `resume`. Unresolved items leave the run at `needs_review`; they must never be silently treated as pass. The merge fidelity audit report is attached before materialization and blocks it when `passed` is false.

## Focused tests / migration order

1. Establish core primitives and schemas with unit tests for canonical serialization, path escape, atomic publish, inventory/hash changes, and stale cache keys.
2. Build a synthetic non-Letter, two-page contract/PDF fixture. Add a runner integration test through prepare -> synthetic MinerU outputs -> compare -> queue -> supplied closed decisions -> audit -> materialize. This both proves a third scenario and forces the generic page-geometry decision.
3. Add negative integration tests: changed source/contract/tool identity, missing/duplicate/open decision, unsafe decision path, missing declared output, and stale stage manifest must fail closed.
4. Add adapter parity tests for the existing three-view CLIs using their unchanged argument/output schemas. Keep current unit suites as component regression.
5. Only after this slice is green, adapt later reconstruction finalization to contract-driven handout requirements and separately plan publication-stage adapters. Do not fold those into Wave 0.

## Wave 0 assessment

Wave 0 can be scoped to this goal without blocking the current read-only reconnaissance: it is limited to the reusable control plane for `reconstructed_en`, uses a synthetic fixture rather than Dissociation facts, and does not require a reviewed Dissociation contract or source generation. Implementation should begin only after the orchestrator/architect records the compatible contract-to-RunSpec boundary and the non-Letter geometry policy. The run itself remains blocked on the reviewed runtime contract and live MinerU/tool discovery, not on this audit.

## Files checked

- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/{plan,context}.md`
- `kb_creator/docs/reviews/KB_CREATOR_PIPELINE_AUTOMATION_REVIEW_20260913.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/contracts/scenario_contract.v1.schema.json`
- `kb_creator/scripts/{scenario_contract,prepare_mineru_three_view_inputs,run_mineru_three_view,compare_mineru_three_views,audit_mineru_ai_merge_fidelity,materialize_mineru_ai_merge,finalize_mineru_reconstruction,reconstruct_scenario_source,scenario_source_reconstruction}.py/.ps1`
- `kb_creator/tests/{test_mineru_three_view_tools,test_audit_mineru_ai_merge_fidelity,test_materialize_mineru_ai_merge,test_scenario_contract,test_scenario_source_reconstruction}.py`

## Verification and evidence

- Static audit confirmed no `kb_creator/__main__.py`, `pipeline/` package, generic run/stage/review-queue schemas, or public top-level runner exists.
- Existing focused tests are present and cover deterministic input preparation/resume, three-view comparison, merge fidelity, materializer fail-closed behavior, and contract validation.
- Test execution was attempted with `py -m pytest` and with the bundled Codex Python. It could not run because the launcher reports no installed Python and the bundled runtime has no `pytest` module. No dependency was installed and no project file was changed.

## Blockers and next action

- Blocker: focused runtime verification is unavailable until an approved test environment with `pytest` and the PDF test dependencies is selected; this does not block the read-only audit.
- Next action: orchestrator/architect should accept or amend the Wave 0 boundary (especially generic page geometry and whether `ScenarioContract.v1` is extended now), then dispatch a bounded implementation packet for only the files and tests above.

- Elapsed time: approximately 17 minutes.
- Token use: unavailable.
