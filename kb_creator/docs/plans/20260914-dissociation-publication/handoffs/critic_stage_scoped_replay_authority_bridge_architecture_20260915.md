# Independent architecture re-review: Packet H replay authority bridge

- **Review kind:** architecture
- **Candidate under review:** `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_stage_scoped_replay_authority_bridge_20260915.md`
- **Related prior artifacts:** original Packet H architecture and `critic_stage_scoped_replay_cache_architecture_20260915.md`
- **Reviewer role requested:** strict independent critic, `gpt-5.5` / medium
- **Actual execution note:** platform-selected model/effort is not directly inspectable here; I did not implement or materially design the candidate.
- **Timestamp:** 2026-09-15T03:33:04.3697318+03:00
- **Assignment state:** complete
- **Orchestrator policy owner:** main-chat orchestrator remains owner; this review does not transfer orchestration or release authority.
- **Scoped override:** architecture re-review only; no implementation edits, no spec edits, no run/source/decision/`.tools` mutation, no network/GPU/remote/API/Git commit.
- **Receipt write scope:** this file only.
- **Elapsed / token evidence:** app goal counter at drafting reported `timeUsedSeconds=122`, `tokensUsed=35605` for this active goal/thread counter.

## Files and evidence checked

Read or inspected:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_stage_scoped_replay_cache_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_stage_scoped_replay_cache_architecture_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_stage_scoped_replay_authority_bridge_20260915.md`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/run.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/outputs/01-prepare-inputs`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/outputs/02-mineru-three-view`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/outputs/03-compare-views`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/outputs/04-visual-merge-bundle`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/mineru_cpu_first.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`

Read-only probes run:

1. Memory quick pass against `C:\Users\user\.codex\memories\MEMORY.md` for Packet H / authority bridge terms returned no relevant hits.
2. Confirmed the new receipt path did not already exist.
3. Re-ran existing production validators against run-07:
   - `reconstruction._validate_live_run_bindings(run_root, run)` passed.
   - `reconstruction._validate_stage_prefix(run_root, run, reconstruction.RUN_STAGES)` passed and returned the four expected Stage 01-04 manifest seals:
     - `01-prepare-inputs` `8CE1FB4231A918A05CAE4E0E5B4057D722854E33AD428895316C832D6CE746BC`
     - `02-mineru-three-view` `0FF911385B13EDF3F524BFA555ED38B8E0AA642903EED341C060390C09FA7A62`
     - `03-compare-views` `C1EA6EF8CF8AC4E978B0FDE59D0A50C8144EF15ABA796DB5C3D5786F58874ABB`
     - `04-visual-merge-bundle` `2AFD79D9AAE71E043162F8C2D31445F95EF9D2EF6E5A20F9CD758CD49922023A`
4. Confirmed Stage 02 has all five planned views: three succeeded CPU views and two skipped optional CUDA views.
5. Scanned run-07 JSON outputs for source-run identity / absolute-path strings. Thirteen JSON files contain run-bound strings and are all covered by the bridge as either rebased wrappers or replay command/execution wrappers:
   - `outputs/01-prepare-inputs/command.json`
   - `outputs/02-mineru-three-view/view-set.json`
   - `outputs/02-mineru-three-view/views/original_hybrid_high/view.json`
   - `outputs/02-mineru-three-view/views/original_pipeline_ocr/view.json`
   - `outputs/02-mineru-three-view/views/original_pipeline_txt/view.json`
   - `outputs/02-mineru-three-view/views/original_vlm/view.json`
   - `outputs/02-mineru-three-view/views/raster_pipeline_ocr/view.json`
   - `outputs/03-compare-views/command.json`
   - `outputs/03-compare-views/comparison.json`
   - `outputs/04-visual-merge-bundle/command.json`
   - `outputs/04-visual-merge-bundle/evidence/execution.json`
   - `outputs/04-visual-merge-bundle/visual/geometry_plan.json`
   - `outputs/04-visual-merge-bundle/visual/visual_manifest.json`
6. String-scan spot checks found no old run identity or absolute path in `outputs/01-prepare-inputs/prepared/sample_pages.json` or Stage 04 merge packet JSON/MD, consistent with the bridge treating them as copied payloads subject to recomputation/path-neutral checks.
7. Rechecked the 19 proposed upstream closure paths from Packet H against run-07 sealed `implementation.files`; all current hashes still matched (`CLOSURE_MATCH_ALL_19`).

## Architecture assessment

The authority bridge closes the previous P1 at the architecture level.

The original Packet H design was unsafe because it required operational output wrappers to remain byte-identical even when those wrappers contained run-07 identity and absolute paths. The bridge replaces that with a clear separation:

- immutable source wrappers are preserved only in `replay/origin/`;
- operational wrappers are deterministically regenerated under fresh run identity;
- every source output row is mapped exactly once to either copied payload or rebased wrapper;
- semantic conservation is proven by typed projections and recomputation, not by trusting stale serialized authority;
- origin strings are never operational paths and no `source_run_root` base exists.

The S1-S4 matrix is adequate for run-07’s actual artifact topology:

- **S1 / Stage 01:** `source_raster.pdf` and `sample_pages.json` are copied only under exact identity/geometry/path-neutral checks; `command.json` is a replay command wrapper.
- **S2 / Stage 02:** all five `view.json` files and `view-set.json` are explicitly rebased, with separate succeeded/skipped projections and no fake argv/stdout/stderr in replay execution; view artifact trees stay byte-identical and contained.
- **S3 / Stage 03:** `comparison.json` is rebased to comparison v3 with fresh refs; semantic projection includes the source/reader payload, pairwise graph and content identities; recomputing `inspect_view` and `diff_blocks` against copied fresh artifacts detects resealed semantic drift.
- **S4 / Stage 04:** geometry, visual manifest, execution and command wrappers are rebased; copied visual payloads and packets are hash/dimension/topology checked, and packets are recomputed from fresh comparison projection and contract roles.

The bridge also resolves P2-H-01 by clarifying that run-07’s historical stage-manifest authority is the sealed `reconstruction.py` validator, not retroactive trust in `stage_manifest.v1.schema.json`. It resolves P2-H-02 by making final live closure proof authoritative after all code lands.

## Findings

### P0

None found.

### P1

None found.

### P2-HR-01 — Make the run-07 wrapper coverage list a required live fixture

The bridge covers every run-bound JSON artifact I found in run-07, but implementation acceptance should freeze that coverage as an explicit fixture/assertion: the thirteen listed run-bound JSON files must either be rebased wrappers or replay command/execution wrappers, and `sample_pages.json` plus all merge packet files must remain path/run-neutral copied payloads unless a future source run proves otherwise.

This is a P2 because the architecture already states conservation and unknown/unregistered files fail; the fixture makes accidental omission easier to catch.

### P2-HR-02 — Clarify `view_artifact_root` as a per-view scoped base

The closed resolver enum includes `view_artifact_root`, but Stage 02 has multiple view artifact roots. The implementation should represent this as a typed per-view authority, for example `(base="view_artifact_root", view_id="<closed view id>", path="<relative>")`, rather than a single ambient base. This prevents accidental cross-view asset resolution while preserving the bridge’s intended containment model.

This is a P2 because later text already says assets resolve via fresh Stage02 root plus the specific view receipt artifact root.

### P2-HR-03 — Keep binary/text copied-payload scans schema-routed

The bridge says copied payload eligibility requires a string scan for source-run identity and absolute paths, while binary/Markdown payloads also rely on stage-specific validators. Implementation should make this routing explicit per artifact type: JSON wrappers require typed schema transforms; Markdown/text copied payloads get deterministic string scans plus semantic recomputation where available; binary/PDF/PNG payloads are not searched as arbitrary text but are validated by bytes/SHA, dimensions, PDF structure, topology and registered semantic validators.

This is a P2 clarification to avoid brittle binary false positives or accidental text payload blind spots.

## Positive evidence

- The bridge forbids the exact unsafe shortcuts that caused the prior NO-GO: stale wrapper-as-authority, global search/replace, fake command execution, source-run-root resolution, and old identity acceptance.
- It preserves `producer_invoked=false` truthfulness and explicitly forbids argv/environment/stdout/stderr in replay execution branches.
- The two-phase graph avoids circular seals: intake has no fresh hashes; rebase receipts and stage manifests seal in dependency order; bridge binds them after Stage 04; review queue is generated after bridge.
- Stage 05/06 remain fresh-only. Decisions, allowlists, candidates, promotion and acceptance are not replayed.
- The downstream resolver contract is appropriately centralized in `validate_replayed_prefix`, returning contained fresh paths so Stage 05/06 cannot accept caller-supplied paths.
- Live run-07 bootstrap remains currently provable under old validators and current closure bytes.
- The implementation packets are additive and explicitly stop with NO-GO if a Stage 01-04 producer-closure file must change.

## Recommendation

**GO for bounded implementation of the remediated architecture**, with P2 clarifications above.

This is not a live replay approval. Live replay remains blocked until HR1-HR3 are implemented, poisoning/semantic/Windows/synthetic/live run-07 tests pass, the Stage 01-04 closure proof still matches, and an independent implementation critic closes P0/P1.

## Go/no-go

- **Bounded implementation of authority bridge architecture:** **GO**
- **Fresh live run from run-07:** **NO-GO pending implementation and independent closure**
- **Run-07 legacy bootstrap status:** currently provable by read-only validators and closure hash comparison; must be re-proven after implementation lands.
