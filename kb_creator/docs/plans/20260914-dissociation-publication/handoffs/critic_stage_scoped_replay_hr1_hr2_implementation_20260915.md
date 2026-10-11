# Independent implementation review: Packet H HR1/HR2 authority bridge

- **Review kind:** implementation
- **Candidate under review:** `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_stage_scoped_replay_authority_bridge_20260915.md` and the bounded HR1/HR2 replay implementation
- **Reviewer role requested:** strict independent critic, `gpt-5.5` / medium
- **Actual execution note:** platform-selected model/effort is not directly inspectable here; I did not implement or materially design the candidate.
- **Timestamp:** 2026-09-15T04:00:54.8525782+03:00
- **Assignment state:** complete
- **Orchestrator policy owner:** main-chat orchestrator remains owner; this review does not transfer orchestration or release authority.
- **Scoped override:** implementation review only; no implementation edits, no run/decision/source/`.tools` mutation, no live replay target, no network/GPU/remote/API/Git commit.
- **Receipt write scope:** this file only.
- **Elapsed / token evidence:** app goal counter at drafting reported `timeUsedSeconds=290`, `tokensUsed=191164` for this active goal/thread counter.

## Files and evidence checked

Read or inspected:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_stage_scoped_replay_authority_bridge_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_stage_scoped_replay_cache_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_stage_scoped_replay_authority_bridge_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_stage_scoped_replay_authority_bridge_architecture_20260915.md`
- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/__main__.py`
- `kb_creator/contracts/reconstruction_stage_dependency_registry.v1.json`
- the 13 replay schemas listed in the engineer receipt
- `kb_creator/tests/test_reconstruction_replay.py`
- run-07 `run.json`, stage manifests and Stage 01-04 outputs under `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07`

Independent checks and probes:

1. Memory quick pass had no relevant HR1/HR2 notes.
2. `pytest` was not available in the bundled Python or MinerU profile Python, so I did not reproduce the pytest suite. I did not install/download anything.
3. `py_compile` passed for:
   - `kb_creator/pipeline/reconstruction_replay.py`
   - `kb_creator/__main__.py`
   - `kb_creator/tests/test_reconstruction_replay.py`
4. JSON parsing passed for the 13 replay schemas and sealed registry JSON.
5. `git diff --check` on the owned replay files returned clean.
6. Replay registry loaded with internal seal `B4F439FDF6425820B41676D5D04F08497838A16989751AC3BE2C4113DD5D244C`.
7. Existing run-07 v1 stage prefix validation passed and returned the known four stage receipts. Old `_validate_live_run_bindings()` now fails `stale implementation`, which is expected after downstream/global inventory changes and is not used as HR1/HR2 authority.
8. New stage-scoped closure proof matched all four registry rows:
   - Stage 01 closure `943B3ED924167FC1648815FA40610C5A2061F5760C7F9773AB832A5A9A9E0B89`
   - Stage 02 closure `E386EB483F76ECD87AEEF267030FB897D0211A88570ED77384D8D7B53233202A`
   - Stage 03 closure `BF1903B2BFB10811D48A69ECFBA53B8C51FD2B3036D4661D82C8C79C4E0C69A6`
   - Stage 04 closure `44DC6F29489E778DA420B02E7BB1528B3ECB01D663CAF72705390B07D0589AC1`
9. `verify_replay_source(... through 04 ...)` passed read-only against run-07 with eligibility seal `6264B4D1A3A5FDD0DB2944F2E925C3DEEDA9673688FE00BE869DADD073115114`.
10. `replay_run_engine(... through 03 ...)` rejected with `partial_prefix_execution_not_implemented` before creating the disposable target.
11. Direct adversarial probes passed for relative-path poison rejection, per-view `view_artifact_root` scoping, JSON/text payload poison rejection, binary scan routing, and absence of Stage05/06/acceptance strings in `reconstruction_replay.py`.
12. Direct adversarial comparison poisoning probe failed the implementation: `_rebase_comparison()` accepted a synthetic old comparison with `root=C:\outside\root` and artifact `path=C:\outside\root\steal.md`, producing a fresh `view_artifact_root` typed ref instead of rejecting.

## Findings

### P0

None found.

### P1-HR1HR2-01 — Origin comparison absolute paths are still used as resolver authority

The bridge architecture requires origin strings to remain opaque: strings inside `replay/origin` or old comparison/visual wrappers must never be passed to `Path`, `open`, subprocess, resolver, or downstream consumer. The implementation violates this in `_rebase_comparison()`:

- it reads old `views.<id>.root` and old `views.<id>.artifacts.<role>.path`;
- it converts them with `Path(...).resolve()`;
- it derives the fresh relative artifact path from those old absolute strings.

Independent adversarial probe:

- source comparison had `root = C:\outside\root`;
- artifact had `path = C:\outside\root\steal.md`;
- `_rebase_comparison()` accepted it and emitted:
  - `{"base":"view_artifact_root","view_id":"v","path":"steal.md",...}`

That is an origin-path poisoning acceptance. It also means the implementation can consult host filesystem path semantics while transforming old wrapper content. This directly violates the authority-bridge invariant and the assignment requirement that the origin vault is never dereferenced and operational paths are fresh-relative only.

Required remediation:

- Do not call `Path`, `resolve`, `relative_to`, or any filesystem/path resolver on old comparison strings.
- Derive artifact relative paths only from sealed source output inventory / view receipt artifact-root inventory / registered relative MinerU artifact names, or reject if no sealed relative mapping exists.
- Add adversarial tests where old `root` and artifact `path` are internally consistent but outside the source run, including drive, UNC, device, traversal, symlink-like and non-existing paths.

### P1-HR1HR2-02 — Stage 04 geometry/visual v2/v3 are generic envelopes, not typed fresh authority wrappers

The remediated architecture requires field-level typed rebasing:

- geometry v2 should carry fresh preparation/comparison/view-set refs, fresh run identity, layout content identities, rendered-page records, source geometry policy/tolerances, and recomputation proof;
- visual bundle v3 should carry fresh typed inputs/layout refs, fresh comparison/view-set/geometry identities, copied-payload inventory identities, replay execution evidence, and a recomputed manifest seal;
- new schemas should forbid absolute-path strings in operational authority fields.

The current implementation uses `_replay_envelope()` for `geometry_plan.json`, `visual_manifest.json`, and `evidence/execution.json`. The corresponding schemas are generic:

- `mineru_geometry_plan.v2.schema.json` requires only `schema`, `run_identity_sha256`, `origin`, `semantic_projection`, `semantic_projection_sha256`, `execution`, `plan_sha256`.
- `mineru_visual_merge_bundle.v3.schema.json` similarly requires only generic `semantic_projection` rather than typed fresh refs.

This is not the field-level S4 transformer specified by the bridge. It may remove stale strings from top-level operational authority, but it does not provide the structured fresh refs and recomputation contract that HR3 downstream adapters would consume. Proceeding to HR3 on top of these envelopes would force HR3 either to parse generic projections or redesign HR1/HR2.

Required remediation:

- Implement explicit geometry v2 and visual bundle v3 structures with closed nested schemas for every operational authority field.
- Regenerate geometry from fresh Stage01/02/03 refs as specified, and validate rendered payload topology/dimensions/hashes.
- Regenerate visual manifest from fresh typed refs and copied-payload inventories, not a generic opaque projection blob.

### P1-HR1HR2-03 — Comparison v3 schema/runtime leaves critical nested authority shapes generic

`mineru_multi_view_comparison.v3.schema.json` closes only the top-level object. Critical nested authority fields remain generic:

- `view_set` is only `"type":"object"`;
- `views` is only `"type":"object"`;
- `pairwise` is only `"type":"array"`.

The runtime does produce some typed refs, but the schema does not enforce the per-view scoped ref shape, and the transformer still uses old absolute paths as described in P1-HR1HR2-01. This is not sufficient HR1 schema/runtime parity for comparison v3.

Required remediation:

- Close `view_set`, `views.<id>.root`, every artifact ref, skipped-view rows, pairwise graph, failures and semantic projection shapes.
- Ensure runtime validation recomputes the projection from the fresh operational wrapper, not merely records equal hashes in the rebase receipt.

### P2-HR1HR2-04 — `verify-source` still reports shorter prefixes as eligible

`replay_run_engine(... through 03 ...)` correctly fails before target creation with `partial_prefix_execution_not_implemented`, satisfying the no-target-mutation part of the bounded implementation. However `verify_replay_source(... through 03 ...)` returns `eligible` for `['01-prepare-inputs','02-mineru-three-view','03-compare-views']`.

If replay v1 is now full-prefix-only, `verify-source` should report unsupported/ineligible for 01/02/03 too, or at minimum return a distinct non-runnable eligibility state. Otherwise operators can receive a positive eligibility report for a replay route that `run` will never execute.

### P2-HR1HR2-05 — Focused pytest suite not independently reproducible in this review environment

The engineer reports 55 focused tests and 166 broad tests passing. I could not independently rerun them because neither the bundled Python nor the MinerU profile Python has `pytest`. I performed compile, schema parse and direct adversarial probes instead. This is an evidence limitation, not itself an implementation defect.

## Positive evidence

- No declared upstream S1-S4 closure member appears changed relative to run-07 for the new stage-scoped closure proof.
- Registry graph and closure rows are sealed and ordered for the four upstream stages.
- Full-prefix run-07 `verify-source` passes read-only with the engineer's eligibility seal.
- `replay_run_engine` rejects 01/02/03 run attempts before target creation.
- Direct path containment probes for fresh typed refs, per-view root scoping and payload scan routing passed.
- Replay module does not contain Stage05/06 or acceptance execution routes.
- Compile, schema JSON parsing and diff-check passed for the reviewed owned files.

## Recommendation

**NO-GO for retaining HR1/HR2 as an implementation closure and NO-GO for proceeding to HR3 on this base.**

The implementation is valuable as a development draft, and the full-prefix fail-fast/closure proof pieces are promising, but HR1/HR2 are not closed because origin path poisoning is accepted and the Stage04/Comparison operational schemas are not the typed authority wrappers required by the accepted bridge architecture.

Recommended next step:

1. Remediate P1-HR1HR2-01 by eliminating all `Path`/resolver use on old origin strings and deriving refs only from sealed relative inventories.
2. Replace generic comparison/geometry/visual envelopes with closed typed schemas and field-level transformers.
3. Make 01/02/03 `verify-source` semantics match the full-prefix-only run semantics or clearly mark them non-runnable.
4. Rerun focused tests plus the specific poisoning probes above, then request another bounded implementation closure before HR3.

## Go/no-go

- **Retain HR1/HR2 as closed:** **NO-GO**
- **Proceed to HR3 downstream adapters on this base:** **NO-GO**
- **Live replay:** **NO-GO**
- **Run-07 legacy bootstrap:** stage-scoped proof currently passes, but it does not overcome the P1 transformer/schema blockers.
