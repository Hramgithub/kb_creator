# Packet H — fail-closed stage-scoped reconstruction replay/cache

## Receipt

- **Timestamp:** 2026-09-15T03:13:56+03:00
- **Role / scoped override:** architecture and dependency analysis, `gpt-5.6-sol` at `high`; read-only work except for this assigned handoff.
- **Orchestrator policy owner:** main-chat `gpt-5.6-sol` at `medium`; orchestration ownership was not transferred.
- **Assignment state:** complete; implementation not started and acceptance not inferred.
- **Scope:** universal, scenario-neutral replay of an exact sealed reconstruction stage prefix so downstream-only code changes do not force MinerU Stages 01-04 to execute again; concrete legacy bootstrap source is immutable Dissociation run `20260915-cpu-first-07`.
- **Result:** **conditional GO** for run-07 as a legacy replay source. Its run seal, live source/contract/tool/provider bindings, all four stage receipts, and every output inventory currently validate. Replay remains blocked until the schemas, canonical producer-dependency registry, engine, and tests below are implemented and independently reviewed.
- **Files changed:** this receipt only.
- **Blockers:** current v1 stage manifests bind the entire run implementation inventory and contain neither a per-stage producer closure nor replay provenance. Existing `run_engine`/`resume_engine` cannot safely author or consume replayed stages.
- **Next action:** implement packets H1-H3 below after or alongside the G1/G2 downstream correction, without modifying any Stage 01-04 producer dependency. Then run the live eligibility command and create a new absent run root by the replay route.
- **Elapsed time:** approximately 35 minutes.
- **Token use:** exact role token count unavailable.

## Current evidence and root cause

The current fixed graph is Stages 01-04 followed by fresh-only Stages 05-06 (`kb_creator/pipeline/reconstruction.py:38-45`). Run construction seals one global implementation inventory (`:287-319`, `:508`, `:567-569`). Every stage cache key and manifest repeats that global inventory hash (`:994-1031`), and validation requires equality to the new run's global hash (`:1122-1155`). Live binding also rejects any global implementation change (`:733-769`). This is correct for resume-in-place, but too coarse for cross-run replay: changing only the Stage 05 auditor invalidates Stages 01-04 even though their producers, inputs, tools, and outputs are unchanged.

The existing output check is reusable evidence: `_validate_stage` rejects wrong roots, reparses, missing/extra/tampered files, or an inventory seal mismatch (`:1156-1182`). Existing invocation uses an isolated staging directory and publishes only after output validation (`:1687-1770`). Packet H must preserve and strengthen these properties; it must not reinterpret v1 `cache_key` as cross-run authority because that key includes the old run identity and global implementation.

### Immutable run-07 witness

- Run identity: `3F7F9B4765D79BCDA5A3BBCC8EAB22723C2063161E2C31B65A3843507F81E40A`.
- Source PDF: 2,159,317 bytes, SHA-256 `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B`.
- Contract: 1,302 canonical bytes, SHA-256 `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E`.
- Sealed implementation inventory: `866FBE68AA8F1E2D517F2791CD76C763421104F5E85870DD199A26855591FB25`; all 30 recorded files were present and byte/hash-identical at the checkpoint.
- Provider capability receipt: `f0925f03ce014e12ff407786286c90db74077f73db00b06153b045957347dccf`; required `pipeline_cpu=ready`; optional CUDA providers remain explicitly unavailable, not silently removed.

| Stage | Source manifest seal | Source output inventory |
|---|---|---|
| `01-prepare-inputs` | `8CE1FB4231A918A05CAE4E0E5B4057D722854E33AD428895316C832D6CE746BC` | `64C43C2A82AE078DFE71B98091998E35F36A276437BFDE7E27A7C52A8F6DAF7D` |
| `02-mineru-three-view` | `0FF911385B13EDF3F524BFA555ED38B8E0AA642903EED341C060390C09FA7A62` | `6CEE0F07679E845763B21A04D9BDAF99614ED261255CDFDEA182F1F828BA7B63` |
| `03-compare-views` | `C1EA6EF8CF8AC4E978B0FDE59D0A50C8144EF15ABA796DB5C3D5786F58874ABB` | `E06E0D3A697D1DF0C3C28E05958D4F53C3E3F1886DE537DF1F626D764F2AB995` |
| `04-visual-merge-bundle` | `2AFD79D9AAE71E043162F8C2D31445F95EF9D2EF6E5A20F9CD758CD49922023A` | `8C9F21589173B42226ADB42219C5E8BE00391294770093B4A76055BAB5FFF806` |

A live read-only call to `load_run`, `_validate_live_run_bindings`, and `_validate_stage_prefix(..., RUN_STAGES)` returned exactly those four receipts. This proves the source is internally valid under the current v1 verifier. It is not yet a replay acceptance or a substitute for the new closure verifier.

## Contract boundary

Replay v1 accepts only one **contiguous prefix** starting at Stage 01 and ending at Stage 01, 02, 03, or 04. The Dissociation request uses the full `01..04` prefix. A gap, reordered stage, stage outside the fixed graph, or request containing Stage 05/06 is invalid. Stages 05 `fidelity_audit` and 06 `materialize_candidate` are always freshly executed from fresh, authority-bound decisions.

A replay creates a new absent run root, fresh run id, fresh portable run identity, and current implementation evidence. It physically materializes byte-identical eligible outputs and authors new stage receipts bound to the new run. It does not resume, mutate, reseal, rename, hardlink, or accept the source run. It regenerates the review queue and draft decision template for the new run and stops at `needs_review`. No old decision, allowlist, audit, candidate, user acceptance, or release state is copied or inferred.

The explicit source run is the cache. No implicit directory scan, newest-run selection, global cache hit, or content-address-only lookup is allowed in v1. An optional exported capsule may be added later only through the same verifier and with an explicit absent destination.

## Canonical producer-dependency closure

Add a static, schema-valid `kb_creator.reconstruction_stage_dependency_registry.v1` document. It is code-reviewed authority, not data inferred from imports at runtime. It contains the exact ordered four stage rows, direct upstream stage ids, relevant run-field selectors, exact repository-relative implementation paths, tool/provider selectors, output validator id/version, argv-recipe version, and a canonical registry seal. Duplicate paths/rows, unknown selectors, dynamic globs, optional omissions, or a registry/run schema pair not explicitly supported fail.

### Common closure for all four stages

The conservative common set is:

- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/identity.py`
- `kb_creator/pipeline/manifests.py`
- `kb_creator/pipeline/mineru_cpu_first.py`
- `kb_creator/pipeline/process.py`
- `kb_creator/pipeline/windows_process_tree.py`
- `kb_creator/contracts/run_spec.v2.schema.json`

It intentionally includes controller/process files even where a narrower import trace might appear sufficient. Changing one invalidates upstream eligibility; safety is preferred over hit rate. `kb_creator/__main__.py` is not a producer after exact parsed run fields are sealed, so the additive replay CLI may change it without invalidating run-07.

### Stage-specific closure and direct data dependencies

| Stage | Additional implementation/schema paths | Direct upstream/output dependencies |
|---|---|---|
| 01 `prepare_inputs` | `scripts/prepare_mineru_three_view_inputs.py`; `contracts/mineru_three_view_inputs.v2.schema.json`; `contracts/mineru_geometry_plan.v1.schema.json` | exact contract and source identities; none upstream |
| 02 `mineru_three_view` | `scripts/run_mineru_three_view.ps1`; `contracts/mineru_view_execution.v1.schema.json`; `contracts/mineru_view_set.v1.schema.json`; `contracts/mineru_three_view_inputs.v2.schema.json`; `MinerU/scripts/probe-capability.ps1` | Stage 01 receipt/output; original PDF and exact prepared raster input |
| 03 `compare_views` | `scripts/compare_mineru_three_views.py`; `contracts/mineru_view_set.v1.schema.json`; `contracts/mineru_multi_view_comparison.v2.schema.json`; `contracts/mineru_three_view_inputs.v2.schema.json` | exact Stage 01 and 02 receipts/outputs |
| 04 `visual_merge_bundle` | `scripts/build_mineru_visual_merge_bundle.py`; `contracts/mineru_three_view_inputs.v2.schema.json`; `contracts/mineru_view_set.v1.schema.json`; `contracts/mineru_multi_view_comparison.v2.schema.json`; `contracts/mineru_geometry_plan.v1.schema.json`; `contracts/mineru_geometry_failure.v1.schema.json`; `contracts/mineru_visual_merge_bundle.v2.schema.json` | exact Stage 01, 02, and 03 receipts/outputs, including prepared manifest and comparison |

For every reused stage, the verifier derives a **source closure** only by selecting those exact paths from the sealed source run implementation inventory. Every registry path must exist exactly once there. It computes `producer_closure_sha256` from ordered `{path,bytes,sha256}` rows. It separately computes the same closure from current checkout bytes. Equality is mandatory.

The following portable run fields must also be exactly equivalent between source and new run: target, profile, contract canonical bytes/hash/revision, source bytes/hash/page geometry, ordered scope, all reconstruction options, execution boundary, view plan, provider capability state and receipts, provider profiles (including Python, MinerU, config, lock/distributions, source and model manifest), common tools, and toolchain. Local/absolute paths, timestamps, run id, run-root path, and human-readable path hints are provenance only and never cache-key material. The current files are read from explicit CLI paths and checked by bytes/hash; path equality is neither required nor trusted.

`stage_eligibility_key` is the canonical hash of: stage id/version/recipe version, exact selected portable fields, current/source-equal producer closure hash, exact relevant tools/providers, direct upstream **output inventory** hashes, and direct input identities. It excludes timestamps, absolute paths, source/new run ids, and execution diagnostics. The new stage receipt is nevertheless bound to both the new run identity and exact source provenance.

## Legacy run-07 bootstrap

Run-07 has v1 stage receipts with a global implementation hash, not per-stage closures. Safe derivation is nevertheless possible because:

1. its full run implementation inventory is sealed and currently validates;
2. every proposed Stage 01-04 closure member is already an exact record in that sealed inventory;
3. each stage receipt binds the expected adapter script hash, ordered upstream receipts, exact inputs/options/tools, and complete output inventory;
4. the canonical registry supplies a conservative, independently reviewed mapping rather than allowing the caller to choose paths.

The legacy derivation algorithm first verifies the old portable run seal, full source stage prefix, old manifest seals, exact on-disk output inventories and semantic stage-output validators. It then selects closure rows from the sealed inventory, verifies the adapter row equals the old stage adapter receipt, and compares every closure/tool/provider/input field with current authority. It must not use the old global `cache_key` as evidence of cross-run eligibility.

If any registry path is missing from the legacy inventory, any dependency is ambiguous, or an old output cannot pass the current non-downgraded semantic validator, run-07 is **not exportable or replayable**. The only alternative is one fresh Stage 01-04 execution under the new receipts, followed by `replay export` to an absent capsule root. Export cannot invent missing legacy evidence, accept a manual file list, or waive a mismatch.

Current verdict is conditional GO because all current run-07 inventory records match and the full source prefix validates. Final GO requires the implemented registry to reproduce that proof after G1/G2 land.

## Schemas and provenance

### `stage_dependency_registry.v1`

Required sealed fields: schema/version; supported source run/stage schema versions; fixed graph; per-stage exact dependency rows described above; closed selector/validator/recipe enums; registry SHA-256. `additionalProperties=false` throughout.

### `stage_replay_plan.v1`

Stored at `replay/plan.json` in the new run and sealed before copying. Required fields:

- new run id and portable run identity;
- replay implementation inventory and registry file identities/seals;
- source run `run.json` identity, source run id and portable identity;
- exact requested prefix;
- exact portable-field equivalence report;
- for each stage: source manifest path/bytes/file SHA and reproducible seal, source output inventory and file rows, source/current closure rows and closure hash, tool/provider/input evidence, eligibility key, destination relative paths;
- ancestry containing the ultimate executed source identity and no duplicates;
- `acceptance_inferred=false`, `decisions_replayed=false`, `stages_05_06_replayed=false`;
- canonical `plan_sha256`.

### `stage_manifest.v2`

Preserve the v1 reproducible stage fields, but replace the ambiguous global producer claim with both:

- `verification_implementation`: current run/global implementation identity plus replay engine/registry/schema identities;
- `producer_closure`: registry identity, exact ordered closure rows, closure hash and recipe version.

`execution.mode` is `executed` or `replayed`. A replayed record requires `producer_invoked=false`, copy timestamps, and `replay_provenance` containing plan seal, source run id/identity, source stage manifest identity/seal, source output inventory hash, copied file inventory hash, and current eligibility key. A fresh Stage 05/06 record requires `mode=executed` and forbids replay provenance. The receipt `reproducible_sha256` binds the new run identity, new upstream receipt chain, exact current inputs, physical output inventory, producer closure, and replay provenance.

The source output files remain byte-identical. Old `command.json` or diagnostic absolute paths are retained as sealed historical producer diagnostics and are never followed or used in identity derivation. All live consumption resolves only canonical relative paths under the new run root.

## CLI and API

Proposed public surface:

```text
python -m kb_creator replay verify-source \
  --contract <current-contract> --source <current-source.pdf> \
  --source-run-root <sealed-run> --through-stage 04-visual-merge-bundle \
  <the existing explicit CPU runtime/tool arguments> --json

python -m kb_creator replay run \
  --contract <current-contract> --source <current-source.pdf> \
  --source-run-root <sealed-run> --run-root <absent-new-root> \
  --run-id <fresh-id> --through-stage 04-visual-merge-bundle \
  <the existing explicit CPU runtime/tool arguments> --json

python -m kb_creator replay export \
  --source-run-root <sealed-run> --capsule-root <absent-root> \
  --through-stage 04-visual-merge-bundle --json
```

No default source run, implicit latest run, `--force`, `--ignore-*`, `--trust`, `--copy-decisions`, or Stage 05/06 choice exists. `verify-source` is read-only and returns a sealed eligibility report to stdout; it does not reserve or create a run root. `run` repeats every validation immediately before copying, so an earlier report is not authorization.

Python API:

```text
verify_replay_source(contract_path, source_path, source_run_root,
                     through_stage, runtime) -> ReplayEligibility

replay_run_engine(contract_path, source_path, source_run_root,
                  new_run_root, new_run_id, through_stage,
                  runtime) -> RunResult(needs_review)
```

If a replayed v2 prefix is present, the CLI dispatches later resume to a replay-aware validator/engine. The old v1 `resume_engine` must reject v2 manifests. The replay-aware resume executes only Stages 05/06 and requires their downstream scripts to validate the v2 prefix and replay plan before reading outputs.

## State machine and atomic materialization

```text
ABSENT
  -> PREFLIGHT_VALIDATED
  -> SOURCE_PREFIX_VALIDATED
  -> CLOSURES_EQUAL
  -> PLAN_SEALED_IN_OWNED_STAGING
  -> FILES_COPIED_AND_REOPEN_VERIFIED
  -> NEW_STAGE_RECEIPTS_SEALED
  -> QUEUE_REGENERATED
  -> WHOLE_RUN_VERIFIED
  -> ATOMIC_PUBLISHED
  -> NEEDS_REVIEW
```

Any transition failure goes to `REJECTED_NO_RUN`. There is no partial success, resume of a failed replay attempt, or fallback to unverified copying.

The final run root must be absent. Work occurs in one exclusive hidden sibling staging root on the same volume, with a random name and a marker binding it to the exact final canonical path and operation id. The engine validates source and destination roots are distinct, neither contains the other, neither is a reparse traversal, and ancestry contains neither self nor duplicate run identities.

Each destination directory is created by the engine. Every artifact is streamed into a new `xb` regular file; symlinks, junctions, mount points, reparse points, hardlinks, alternate data streams, device names, `..`, absolute paths, trailing-dot/space aliases, reserved names and Windows case-fold collisions are rejected. Do not use hardlink/reflink/dedup APIs. After every write: flush, OS-level durability flush where supported, close, reopen without following reparses, recompute bytes/SHA, and require a distinct file identity from the source. Recompute the whole deterministic inventory after copy.

Only after the complete staged run, stage receipts, replay plan, regenerated queue and decision template validate is the sibling directory published with same-volume rename-no-replace. On pre-publish failure, remove only the marker-owned staging root. If post-rename reopen verification ever fails, move the final root by rename-no-replace to an operation-specific quarantine and report failure; never leave the requested target usable and never delete or alter the source. A successful target is immutable.

## Tamper, mismatch and downgrade rejection

Reject before destination publication on any of the following:

- missing/extra/reordered requested stage; partial prefix; Stage 05/06 request;
- source/new root equality, nesting, ancestry cycle, replay-of-self, or duplicate ancestor identity;
- unsupported or downgraded run/stage/registry/recipe/output schema or validator version;
- stale/tampered run seal, manifest seal, upstream receipt, input, output file, output inventory, registry or plan;
- source PDF/contract/target/scope/options/view plan/execution boundary mismatch;
- provider state/profile/receipt/model/lock/distribution or tool bytes/hash mismatch;
- missing, extra, ambiguous, or changed producer-closure member;
- adapter hash differing from registry/source/current closure;
- old path-dependent diagnostics being followed, rewritten, or used as current authority;
- source file reparse/hardlink/ADS/case alias, destination escape, copy verification failure, or pre-existing target;
- any attempt to replay decisions, allowlist, review acceptance, Stage 05 audit, Stage 06 candidate, promotion or release evidence.

The engine emits stable reason codes, never a best-effort hit. Rejection may recommend fresh upstream execution but may not silently execute it.

## G1/G2 sequencing without invalidating upstream eligibility

The Packet G corrections belong to the Stage 05 closure: `audit_mineru_ai_merge_fidelity.py`, its audit/allowlist schemas, and focused tests. They are deliberately absent from every Stage 01-04 closure above. Therefore they may land before replay and change the new run's global/current implementation identity without changing an upstream eligibility key.

Packet H implementation must likewise be additive: new replay module, static registry, new schemas, tests, and CLI dispatch in `kb_creator/__main__.py`. It must not edit `reconstruction.py`, `identity.py`, `manifests.py`, `mineru_cpu_first.py`, process-tree code, Stage 01-04 scripts, or their schemas. If implementation discovers that one of those files must change, run-07 eligibility becomes NO-GO and Stages 01-04 must execute once under the new producer closure.

The Stage 05 auditor and Stage 06 materializer may be changed to call the replay-aware verifier; both are downstream producer closures and must execute fresh. Existing decisions cannot be reused as authority merely because page packets are byte-identical. New decisions/allowlist must bind the fresh queue, comparison, visual identities and new run identity.

## Tests and acceptance criteria

### Static/contract tests

1. Registry schema is closed, exactly four ordered stages, exact path rows/selectors, no duplicates/globs, and a verified canonical seal.
2. AST/import policy proves replay code cannot request Stage 05/06, call acceptance/promotion code, follow old absolute diagnostics, or invoke a remote endpoint.
3. A change to either G1/G2 Stage 05 file leaves all four upstream eligibility keys unchanged; a one-byte change to every individual upstream closure member invalidates every affected stage and dependent suffix.
4. `__main__.py`/replay-engine-only change does not alter producer keys but does change replay verification implementation identity.

### Synthetic E2E

5. Execute synthetic Stages 01-04 once, replay them into a fresh root, prove byte-identical per-stage outputs, distinct physical file ids, new run/stage seals, explicit source provenance, regenerated queue, and terminal `needs_review` with no acceptance text.
6. Resume that replay run with fresh closed decisions; assert Stage 05 and 06 adapters are invoked exactly once and Stages 01-04 adapters zero times.
7. Prefix cases 01, 01-02, 01-03, 01-04 either replay the exact requested prefix and freshly execute the remainder through Stage 04 or fail without a target; gaps/reordering always fail.
8. Inject failure at each validation/copy/flush/seal/rename boundary; assert requested final root absent or quarantined, owned staging cleaned, source unchanged, no partial stage visible.

### Adversarial matrix

9. One case for every run field, provider/tool identity, closure member, adapter, upstream receipt, input, output row/hash/order, registry/plan seal and source schema/version mismatch; all fail before publish.
10. Missing/extra file, resealed semantic tamper, source-stage partiality, stale source/contract, source/destination reparse, symlink/junction, hardlink, ADS, device name, case collision, traversal, nested roots, self replay and ancestry cycle all fail.
11. A fully rehashed but semantically changed output fails the current stage semantic validator; resealing is never sufficient.
12. Legacy inventory missing one registry member cannot be repaired by export or caller override; only a new executed upstream run becomes exportable.

### Live run-07 proof

13. Rerun read-only legacy validation after G1/G2 and Packet H land; require the four source manifest/output identities listed above and exact current/source closure equality.
14. Create a fresh absent Dissociation run root using `--through-stage 04-visual-merge-bundle`; prove all output files physically materialized and byte-identical, every new receipt binds run-07 provenance, no source file changed, no Stage 05/06 output exists, and result is `needs_review`.
15. Verify the new queue/decision template bind only the new run. Old run-07 decisions and allowlist must fail against it until deliberately re-authored/revalidated.

Acceptance requires focused replay tests, the complete existing reconstruction suite, Windows containment tests, synthetic E2E, live run-07 eligibility proof, and a separate independent critic review with no P0/P1. This architecture receipt is not that review.

## Implementation packets

### H1 — contracts and registry

Owned files: new static dependency registry plus `stage_dependency_registry.v1`, `stage_replay_plan.v1`, and `stage_manifest.v2` schemas; focused schema/registry tests. No pipeline or run edits. Deliver a critic-reviewed exact registry before live use.

### H2 — verifier, materializer and CLI

Owned files: new `kb_creator/pipeline/reconstruction_replay.py`, additive CLI dispatch, and focused replay tests. Reuse existing identity/containment primitives read-only; keep all Stage 01-04 producer files byte-identical. Implement verify-source, run, optional export, atomic physical copying and replay-aware Stage 05/06 resume. No scenario-specific code.

### H3 — QA and live eligibility

Run the full adversarial/synthetic matrix, existing reconstruction regressions, and read-only run-07 eligibility proof. Only after independent implementation closure may an executor create the fresh replayed Dissociation run. Decisions, Stage 05/06, promotion and publication remain separate gates.

## Files checked

- Current Dissociation plan/status and NRI governance/role boundary.
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`.
- `kb_creator/pipeline/reconstruction.py`, `mineru_cpu_first.py`, identity/process/manifest boundaries, and CLI routing.
- Current run/stage schemas and reconstruction/MinerU tests.
- Run-07 `run.json`, Stage 01-04 manifests, output inventories, provider/tool evidence, comparison and visual bundle identities.
- Packet G completeness remediation, specifically the downstream-only G1/G2 boundary.

## Verdict

**Architecture GO; live replay conditional GO.** A universal fail-closed replay is feasible without repeating MinerU when producer equivalence is stage-scoped, conservative and exact. Run-07 contains enough sealed legacy evidence for bootstrap through the canonical registry, and it currently validates. The mechanism must be implemented and independently reviewed first. G1/G2 may safely land before replay only if they remain in the downstream Stage 05 closure and Packet H remains additive. Any change to an upstream closure member converts the verdict to **NO-GO for run-07** and requires one fresh Stage 01-04 execution. Stage 05/06, decisions and acceptance are never replayed.
