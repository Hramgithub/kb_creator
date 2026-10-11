# Independent architecture review: Packet H stage-scoped replay cache

- **Review kind:** architecture
- **Candidate under review:** `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_stage_scoped_replay_cache_20260915.md`
- **Reviewer role requested:** strict independent critic, `gpt-5.5` / medium
- **Actual execution note:** platform-selected model/effort is not directly inspectable here; I did not implement or materially design the candidate.
- **Timestamp:** 2026-09-15T03:21:11.1999714+03:00
- **Assignment state:** complete
- **Orchestrator policy owner:** main-chat orchestrator remains owner; this review does not transfer orchestration or release authority.
- **Scoped override:** architecture review only; no implementation edits, no run/source/decision/`.tools` mutation, no network/GPU/remote/API/Git commit.
- **Receipt write scope:** this file only.
- **Elapsed / token evidence:** app goal counter at receipt drafting reported `timeUsedSeconds=212`, `tokensUsed=288176` for this active goal/thread counter.

## Files and evidence checked

Read or inspected:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/README.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_stage_scoped_replay_cache_20260915.md`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/run.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/stages/*/stage.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/outputs/01-prepare-inputs`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/outputs/02-mineru-three-view`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/outputs/03-compare-views`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/outputs/04-visual-merge-bundle`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/mineru_cpu_first.py`
- `kb_creator/pipeline/identity.py`
- `kb_creator/pipeline/manifests.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`

Read-only probes run:

1. `git status --short --branch` confirmed a dirty worktree existed before this review. I treated all existing changes as out of scope and did not edit them.
2. `Test-Path` confirmed this receipt did not previously exist.
3. Run-07 shape inspection confirmed `run.json`, `stages/`, `outputs/`, and `review/`; `outputs/` contains only `01-prepare-inputs` through `04-visual-merge-bundle`.
4. Hash comparison of the Packet H proposed Stage 01-04 closure paths against run-07 sealed `implementation.files` showed `MATCH` for all checked closure members:
   - `kb_creator/pipeline/reconstruction.py`
   - `kb_creator/pipeline/identity.py`
   - `kb_creator/pipeline/manifests.py`
   - `kb_creator/pipeline/mineru_cpu_first.py`
   - `kb_creator/pipeline/process.py`
   - `kb_creator/pipeline/windows_process_tree.py`
   - `kb_creator/contracts/run_spec.v2.schema.json`
   - `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
   - `kb_creator/contracts/mineru_three_view_inputs.v2.schema.json`
   - `kb_creator/contracts/mineru_geometry_plan.v1.schema.json`
   - `kb_creator/scripts/run_mineru_three_view.ps1`
   - `kb_creator/contracts/mineru_view_execution.v1.schema.json`
   - `kb_creator/contracts/mineru_view_set.v1.schema.json`
   - `MinerU/scripts/probe-capability.ps1`
   - `kb_creator/scripts/compare_mineru_three_views.py`
   - `kb_creator/contracts/mineru_multi_view_comparison.v2.schema.json`
   - `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
   - `kb_creator/contracts/mineru_geometry_failure.v1.schema.json`
   - `kb_creator/contracts/mineru_visual_merge_bundle.v2.schema.json`
5. Existing production validators passed read-only:
   - `reconstruction._validate_live_run_bindings(run_root, run)`
   - `reconstruction._validate_stage_prefix(run_root, run, reconstruction.RUN_STAGES)`
   - Returned receipts:
     - `01-prepare-inputs` `8CE1FB4231A918A05CAE4E0E5B4057D722854E33AD428895316C832D6CE746BC`
     - `02-mineru-three-view` `0FF911385B13EDF3F524BFA555ED38B8E0AA642903EED341C060390C09FA7A62`
     - `03-compare-views` `C1EA6EF8CF8AC4E978B0FDE59D0A50C8144EF15ABA796DB5C3D5786F58874ABB`
     - `04-visual-merge-bundle` `2AFD79D9AAE71E043162F8C2D31445F95EF9D2EF6E5A20F9CD758CD49922023A`
6. Control-plane inspection confirmed current `RUN_STAGES` are only `prepare_inputs`, `mineru_three_view`, `compare_views`, `visual_merge_bundle`; `RESUME_STAGES` are `fidelity_audit`, `materialize_candidate`.
7. Evidence search found source-run identity and absolute-path payloads inside copied Stage 02-04 outputs:
   - `outputs/02-mineru-three-view/view-set.json:3` contains run-07 `run_identity_sha256`.
   - Stage 02 `views/*/view.json` contain run-07 `run_identity_sha256`, source/input paths, `.tools` paths, and closed invocation diagnostics.
   - `outputs/03-compare-views/comparison.json:4` contains run-07 `run_identity_sha256`; lines 6, 11, 50-58 and later view rows contain run-07 absolute paths.
   - `outputs/04-visual-merge-bundle/visual/geometry_plan.json:4` contains run-07 `run_identity_sha256`.
   - `outputs/04-visual-merge-bundle/visual/visual_manifest.json:5-37` contains absolute paths to run-07 outputs and the original source path.
   - `outputs/04-visual-merge-bundle/evidence/execution.json` contains absolute source-run command paths and staging paths.
8. Downstream current production checks are fresh-run-bound:
   - `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py` requires comparison `run_identity_sha256 == run["portable_identity_sha256"]`.
   - `kb_creator/scripts/materialize_mineru_ai_merge.py` requires `visual.inputs.raw_root` and `visual.inputs.comparison/raw_receipt` to equal the fresh run-local expected paths and requires `geometry.run_identity_sha256 == run["portable_identity_sha256"]`.

## Findings

### P0

None found.

### P1-H-01 — Byte-identical replay outputs are source-run-bound, but the architecture does not define a safe fresh-run authority bridge

Packet H correctly identifies that existing v1 manifests bind a global implementation inventory and proposes new v2 replay receipts bound to a fresh run identity. The source outputs that Packet H proposes to copy byte-identically, however, are not identity/path-neutral. Run-07 Stage 02, Stage 03, and Stage 04 payloads embed the source run identity and absolute source-run paths.

This conflicts with two Packet H requirements unless explicitly resolved:

- fresh replay run identity/provenance;
- no path-dependent identities / no following old absolute diagnostics;
- byte-identical physical copy of Stage 01-04 outputs;
- fresh Stage 05/06 execution from the replayed prefix.

Current downstream code demonstrates the breakage risk: Stage 05/06 validators require the comparison, visual manifest, and geometry plan to bind the fresh run identity and fresh run-local paths. A byte-identical copy from run-07 will either fail those checks or tempt implementation to trust/follow old absolute paths from copied JSON. Packet H says replay-aware resume must validate the v2 prefix and replay plan before reading outputs, but it does not state the normative rule for these source-bound fields.

Required remediation before bounded implementation:

1. Define an explicit replay-aware authority bridge for source-bound payload fields. It must say whether embedded v1 output `run_identity_sha256` and absolute paths are:
   - immutable source provenance only, never dereferenced or used for fresh-run identity, with all operational authority derived from the v2 stage receipt/replay plan and fresh run-local relative paths; or
   - rewritten/normalized into new run-local sidecars, in which case the architecture must stop claiming byte-identical replay for those rewritten artifacts and must seal both copied source payloads and normalized authority sidecars.
2. Require Stage 05/06 to consume only the fresh replay plan, v2 stage receipts, fresh review queue, and fresh run-local relative paths when resolving files, while comparing copied payload hashes as evidence only.
3. Add adversarial tests for stale absolute paths and stale source-run identity in `view-set.json`, `comparison.json`, `geometry_plan.json`, `visual_manifest.json`, and execution diagnostics. Tests must prove these fields cannot authorize file reads outside the fresh run root and cannot masquerade as fresh-run identity.
4. State how existing current checks such as comparison `run_identity_sha256`, visual `raw_root`, geometry `run_identity_sha256`, and materializer raw-root authority are replaced or wrapped in replay-aware validation.

Without this, the design is not safe to implement for a fresh `20260915-cpu-first-07` replay route.

### P2-H-01 — Stage schema identity should be explicit in the replay registry/verification evidence

The spec requires supported source run/stage schema versions and introduces `stage_manifest.v2`, but the closure table does not explicitly include or exclude `kb_creator/contracts/stage_manifest.v1.schema.json`. Current v1 validation is primarily code-driven, yet the repository has a stage schema file and Packet H will add schema-governed v2 manifests.

Recommended remediation: make the registry/eligibility report explicitly bind the accepted stage-manifest schema authority, or explicitly declare the current v1 stage schema file non-authoritative and explain that validation is by the sealed `reconstruction.py` code path. This reduces downgrade/tamper ambiguity.

### P2-H-02 — G1/G2 sequencing should be phrased as live closure proof, not packet-label proof

The spec says G1/G2 corrections are downstream-only and therefore do not invalidate upstream eligibility. My current evidence is compatible with that claim: the Packet H Stage 01-04 closure paths all match run-07, and the visible dirty G1/G2-style file `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py` is outside the proposed Stage 01-04 closure.

Recommended clarification: make the final authority the live registry proof after all packets land, not the packet name or intent. Any actual G1/G2 or Packet H implementation change to `reconstruction.py`, `identity.py`, `manifests.py`, `mineru_cpu_first.py`, process-tree code, Stage 01-04 scripts, or listed schemas must remain an automatic NO-GO for run-07 replay.

## Positive evidence

- The run-07 source is internally valid under current v1 validators.
- The proposed conservative Stage 01-04 implementation closure rows are present in the sealed run-07 global inventory.
- Current checkout bytes for the proposed closure rows match run-07 sealed bytes.
- Existing control plane already separates the four upstream `RUN_STAGES` from `RESUME_STAGES`.
- The architecture correctly rejects Stage 05/06 replay, decision replay, acceptance inheritance, non-contiguous prefixes, global cache-key reuse, and caller-chosen legacy file lists.
- The architecture correctly requires fail-closed Windows containment and atomic physical copying rather than hardlinks or mutation.

## Recommendation

**NO-GO for bounded implementation as written.**

The core stage-scoped closure/bootstrap idea is sound and run-07 has enough current sealed evidence for a legacy eligibility proof, but Packet H must first resolve P1-H-01: byte-identical copied outputs contain source-run identity and absolute paths while downstream fresh execution requires fresh-run authority. After the architecture explicitly defines the replay-aware authority bridge and tests for stale-path/stale-identity handling, I would expect a revised architecture to be implementable without repeating MinerU, provided the live closure equality proof still passes.

## Go/no-go

- **Bounded implementation of current Packet H spec:** **NO-GO**
- **Fresh replay/live use from run-07:** **NO-GO until P1-H-01 is remediated and implementation closure passes**
- **Need fresh Stage 01-04 execution now:** not proven by this review; current closure equality passes. The blocker is architecture authority for replayed source-bound payloads, not a current closure mismatch.
