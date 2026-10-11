# Packet H remediation — replay authority bridge

## Receipt

- **Timestamp:** 2026-09-15T03:27:25+03:00
- **Role / scoped override:** architecture/remediation specification, `gpt-5.6-sol` at `high`; read-only investigation except this assigned receipt.
- **Orchestrator policy owner:** main-chat `gpt-5.6-sol` at `medium`; ownership was not transferred.
- **Assignment state:** complete; supersedes the byte-identical-operational-output claim in Packet H, but does not implement or accept replay.
- **Scope:** close critic P1-H-01 and clarify P2-H-01/H-02 for the immutable Dissociation run `20260915-cpu-first-07`.
- **Result:** adopt a typed replay-aware authority bridge. Immutable content payloads may be copied byte-identically; run-bound JSON/manifests are preserved as opaque origin evidence and deterministically regenerated under the fresh run identity with contained relative references. No source-run path or identity is accepted as current authority.
- **Files changed:** this receipt only.
- **Blocker:** no replay implementation/live run is authorized until the schemas, typed transformers, validators and adversarial tests below receive independent closure.
- **Next action:** bounded implementation packets HR1-HR3, followed by independent critic review and a fresh live closure/eligibility proof.
- **Elapsed time:** approximately 30 minutes.
- **Token use:** exact role token count unavailable.

## Critic finding accepted

The first Packet H design correctly separated Stage 01-04 producer closures from downstream code, but incorrectly required every operational output to remain byte-identical. Run-07 Stage 02-04 authority wrappers are not portable:

- `outputs/02-mineru-three-view/view-set.json` and every `views/*/view.json` contain run-07 `run_identity_sha256`; succeeded view diagnostics also contain source, staging, tool and runtime absolute paths.
- `outputs/03-compare-views/comparison.json` contains run-07 identity plus absolute paths for the preparation manifest, view set, view roots and artifacts.
- `outputs/04-visual-merge-bundle/visual/geometry_plan.json` contains run-07 identity and old Stage 02/03 wrapper identities.
- `visual/visual_manifest.json` and `evidence/execution.json` contain absolute source/run/tool/staging paths.

Current validators correctly require fresh authority: comparison identity at `audit_mineru_ai_merge_fidelity.py:399-405`; fresh raw/comparison paths and geometry identity at `materialize_mineru_ai_merge.py:210-286`; Stage 02/03/04 run identities and wrapper relations at `mineru_cpu_first.py:467-562`, `:565-648`, and `:693-782`. Accepting the old values would be a stale-authority bypass. Following the old paths would be an external-read vulnerability.

## Corrected invariant

Replay conserves **semantic payload**, not necessarily serialized authority wrappers.

```text
sealed source stage
  -> opaque origin evidence (unchanged bytes, never dereferenced)
  -> typed schema-aware transformer
  -> fresh run-local authority wrapper
  -> semantic projection equality + complete conservation proof
  -> fresh stage seal
```

Every source output-inventory row is accounted for exactly once as either:

1. `copied_payload`: byte-identical regular file at its canonical operational path; or
2. `rebased_wrapper`: original bytes copied to the sealed `replay/origin/` vault and a fresh typed wrapper generated at the operational path.

No row may be dropped, multiply mapped, or silently reclassified. New bridge/receipt files are separately inventoried as replay evidence. The complete source stage output inventory remains bound in the replay intake, so regeneration cannot hide an omitted source artifact.

An artifact is eligible for `copied_payload` only when its registry rule and a full recursive string scan prove it contains neither the source run identity nor an absolute/UNC/device/staging path in an authority-bearing field. Unknown JSON shape, extra key, unexpected absolute string, or an unregistered file is NO-GO. Binary/Markdown payloads are still validated by exact bytes/SHA and their stage-specific semantic validators.

## Origin vault and current authority

The new run contains:

```text
replay/
  intake.json
  origin/stages/<stage-id>/stage.json
  origin/wrappers/<stage-id>/<original-relative-path>
  stages/<stage-id>/rebase.json
  bridge.json
```

Origin files are byte-identical evidence only. Their records carry exact source path-within-run, bytes and SHA-256, source run id/portable identity, source stage manifest file identity and reproducible seal, and source output inventory hash. Validators may open an origin file only to hash or parse it inside a typed transformer/projection; strings inside it are never passed to `Path`, `open`, subprocess, resolver or downstream consumer.

Operational authority consists only of the fresh `run.json`, fresh Stage v2 manifests, fresh rebase receipts, final bridge, fresh review queue, and fresh run-local outputs. Every operational reference is a typed POSIX relative reference:

```json
{"base":"run_root","path":"outputs/03-compare-views/comparison.json"}
```

Allowed bases are a closed enum (`run_root`, `stage_01_root`, `stage_02_root`, `stage_03_root`, `stage_04_root`, `view_artifact_root`). Resolution joins the fresh canonical base and relative path, rejects backslashes, colons, empty/dot/dot-dot segments, absolute/UNC/device paths, reparses and escapes, then verifies bytes/SHA. There is no `source_run_root` base. External source/contract/tool files are resolved only from the fresh run's live bindings and checked against their fresh sealed identities; wrapper text never supplies those paths.

## Artifact classification and field-level rebase rules

### Stage 01 `prepare_inputs`

| Artifact | Treatment | Rule |
|---|---|---|
| `prepared/source_raster.pdf` | copied payload | Exact bytes/SHA; rerun current raster-PDF structural verification against the fresh source geometry. |
| `prepared/sample_pages.json` | copied payload if path-neutral | Exact schema/key validation, source bytes/SHA/page topology/render recipe equality, and no stale run/path strings. Otherwise NO-GO; there is no generic JSON rewrite. |
| `command.json` | rebased wrapper | Preserve original opaque; generate `kb_creator.replay_command.v1` stating Stage 01 producer was not invoked, fresh relative input/output refs, origin command identity and transformer id. Do not fabricate a fresh argv. |

### Stage 02 `mineru_three_view`

| Artifact | Treatment | Canonical rebase |
|---|---|---|
| `views/<view>/artifacts/**` | copied payload | Byte-identical physical copy. Exact relative inventory must equal the source view receipt. Content-list image references remain relative to that view's artifact root and are containment-checked. Any absolute or source-run-bearing authority field makes the source ineligible unless a separate registered typed transformer exists. |
| five `views/<view>/view.json` | rebased wrappers | Parse exact v1 shape. Preserve view id, required/provider ids, input identities, execution profile, capability/provider/profile identities, state/reason, artifact-root logical ref, output inventory, page coverage, exit code and blocked-by semantics. Replace `run_identity_sha256` with fresh identity; recompute input references against fresh source/Stage 01; replace old diagnostics with `{mode:"replayed", producer_invoked:false, origin_execution:<opaque identity>}`; recompute cache key and receipt seal. Add origin receipt identity and semantic projection hash. Succeeded and skipped views have separate closed projections. |
| `view-set.json` | rebased wrapper | Preserve ordered plan and succeeded/skipped membership. Replace run identity; replace every receipt row with fresh view-receipt relative path, bytes/SHA and fresh receipt seal; add origin identity/projection; recompute view-set seal. |
| `command.json` | rebased wrapper | Fresh replay-command record only; no copied/fake invocation. |

Use `mineru_view_execution.v2` and `mineru_view_set.v2`. Their `execution.mode="replayed"` branch requires `producer_invoked=false` and forbids argv, environment, stdout/stderr or absolute path fields. The full old diagnostic is retained only as opaque origin bytes.

### Stage 03 `compare_views`

| Artifact | Treatment | Canonical rebase |
|---|---|---|
| `comparison.md` | copied payload | Byte-identical only after scan proves it is path/run-neutral and its status agrees with the fresh comparison. |
| `comparison.json` | rebased wrapper/content index | Parse exact v2 shape. Set fresh run identity. Convert `manifest` and `view_set` to typed fresh relative refs and fresh identities/seals. Update skipped-view receipt rows to fresh Stage 02 receipt identities. Convert each `views.<id>.root` and `views.<id>.artifacts.<role>` to typed refs relative to fresh Stage 02/view artifact roots. Preserve exactly: status, required/succeeded order, skipped view id/reason, coverage, block counts, text lengths, every block/asset-relative reference, pairwise data and failures. Add origin identity, semantic projection hash and a fresh comparison seal. |
| `command.json` | rebased wrapper | Fresh replay-command record; old command opaque only. |

Use `mineru_multi_view_comparison.v3`. The semantic projection excludes authority envelope fields but includes every reader/source datum: required/succeeded/skipped semantics, per-view artifact **content identities**, coverage, counts, lengths, blocks and asset refs, full pairwise graph, status and failures. Source-v2 and fresh-v3 projections must be byte-identical canonical JSON and share one SHA-256. Merely matching block counts is insufficient.

The transformer also reruns `inspect_view` over the physically copied fresh Stage 02 artifact roots and recomputes `diff_blocks`; both must exactly equal the preserved projection. Thus a fully resealed altered comparison cannot pass.

### Stage 04 `visual_merge_bundle`

| Artifact | Treatment | Canonical rebase |
|---|---|---|
| rendered page PNGs, triptychs, contact sheets | copied payload | Exact bytes/SHA/dimensions; validate complete expected page/view topology. |
| merge packet page JSON/MD and merge indexes | copied payload | Exact bytes/SHA after path/run-neutral scan. Recompute every packet from the fresh comparison semantic projection and contract page roles; byte equality is mandatory. |
| `visual/geometry_plan.json` | rebased wrapper | Use `mineru_geometry_plan.v2`. Set fresh run identity; bind fresh preparation/comparison/view-set refs and identities; retain source identity, geometry policy, DPI, tolerances, renderer identity/recipe, succeeded views, layouts' content identities, observed geometry, targets, transforms and rendered-page content records; recompute from fresh inputs and seal. Add origin/projection identity. |
| `visual/visual_manifest.json` | rebased wrapper | Use `mineru_visual_merge_bundle.v3`. All inputs/layouts become typed fresh relative refs or identity-only source/contract/tool records. Update comparison, view-set and geometry bytes/hashes/seals. Preserve counts and copied-payload inventory identities; replace the geometry row with its fresh identity. `execution` becomes replay evidence (`producer_invoked=false`, origin execution identity, renderer recipe/tool identity), never rewritten commands. Recompute complete inventory and manifest seal. |
| `evidence/execution.json` | rebased wrapper | Use `visual_replay_execution.v1`: no commands/environment; bind exact origin execution bytes/SHA, renderer recipe/tool identity, copied render inventory and `producer_invoked=false`. |
| `command.json` | rebased wrapper | Fresh replay-command record; old command opaque only. |

The new geometry and visual schemas forbid absolute-path strings anywhere. Current Stage 04 recomputation is retained: geometry is rebuilt from the fresh preparation manifest, copied layout PDFs, fresh comparison/view set, fresh source identity and current exact renderer; rendered pixels are not regenerated, but their dimensions/hashes and complete topology are reverified.

## Fresh seals and conservation proof

Each `stages/<id>/rebase.json` uses closed schema `kb_creator.stage_rebase_receipt.v1` and contains:

- fresh run identity and intake seal;
- source run/stage manifest identities and source output inventory;
- exact `copied_payload` mappings `{source row, destination row}` with equal bytes/SHA;
- exact `rebased_wrapper` mappings `{source row, origin-vault row, transformer id/version, fresh row, source_projection_sha256, fresh_projection_sha256}`;
- exact fresh operational inventory and its hash;
- `producer_invoked=false`, `semantic_content_changed=false`, `acceptance_inferred=false`;
- canonical receipt seal.

Source and fresh projection hashes must be equal for every transformed semantic wrapper. Command/execution wrappers have no semantic-output projection; their conservation proof is the opaque origin identity plus explicit fresh replay status, not a claim that a command ran.

The fresh Stage v2 manifest binds the fresh run identity, fresh upstream Stage v2 receipts, current producer-closure equivalence, exact operational output inventory, intake identity and its per-stage rebase receipt. It does not claim that the old source manifest was freshly executed.

## Two-phase identity graph (no circular seal)

1. **Intake:** validate the complete legacy source run/stage/output/closure graph and write sealed `replay/intake.json`. It binds the new run identity, source authority, transformation registry and expected mappings, but no fresh output hashes.
2. **Payload phase:** physically copy path-neutral payloads and origin wrappers into the owned staging root; reopen/hash every file.
3. **Stage rebase phase:** in dependency order, generate operational wrappers, compute semantic projections, write a sealed per-stage `rebase.json`, then write that fresh stage manifest. A stage may bind only already sealed upstream stages.
4. **Bridge index:** after Stage 04, write sealed `replay/bridge.json` binding intake, all origin inventories, all four rebase receipts, fresh stage manifests and operational inventories. Stage receipts do not point back to this later index, so no cycle exists.
5. **Review phase:** generate `review_queue.v2` and draft decision template bound to fresh run, fresh comparison/visual identities and the final bridge identity. Stage 05/06 require the same bridge.

No hash placeholder, mutable post-seal field, self-hash exception beyond the standard named seal field, or second-pass mutation is allowed.

## Replay-aware validators and downstream resolution

Add a single entry point:

```text
validate_replayed_prefix(run_root, expected_through=04)
  -> FreshReplayAuthorities
```

It validates fresh run/live bindings, intake/registry/closure equivalence, the complete origin conservation graph, every Stage v2/rebase seal, semantic projections, fresh operational inventories and bridge. It returns already-resolved, contained fresh paths for Stage 02 root, comparison, merge packets, visual manifest and geometry plan. Callers cannot supply or override these paths.

Stage 03 validation reads only fresh Stage 01/02 refs and copied payloads; it never follows origin-v1 fields. Stage 04 validation reads only fresh Stage 01-03 refs. The Stage 05 auditor must replace its direct legacy prefix call with the replay-aware entry point when Stage v2 is detected, then require comparison v3 `run_identity_sha256 == fresh run identity`, fresh comparison seal/projection and fresh packet equality. It still uses exact fresh queue/decision/allowlist authority.

Stage 06 materializer must receive paths only from `FreshReplayAuthorities`. It must remove comparisons against absolute strings embedded in visual v2 and instead require visual v3 typed refs to resolve to those exact fresh contained paths and hashes. Content-list assets resolve as `fresh Stage02 root / view receipt artifact_root / relative asset path`, never as a raw `Path(value)` from origin JSON. Geometry must carry the fresh identity and fresh comparison/view-set identities. Stage 05/06 reject a replay bridge whose operational tree contains comparison/geometry/view-set old identity, any absolute reference, or any source-run identity in an authority field.

Legacy executed-run validation remains unchanged for v1/v2 artifacts. Replay schemas are selected only by fresh Stage v2 manifests plus a valid bridge; a caller cannot mark an arbitrary legacy output as replayed.

## Stage-manifest schema authority clarification

For legacy run-07, the historical authority is the sealed `reconstruction.py` v1 parser/validator in its run implementation inventory. `contracts/stage_manifest.v1.schema.json` was not in that historical inventory and is therefore supplementary documentation, not retroactively trusted producer evidence. Its current SHA-256 `7B9CBEE6DBC4DFD7F0787EB9662BBEA0513416319B5262516B6DB4008004CCB7` may be recorded as current parity evidence, but cannot repair a legacy mismatch.

For replay, `stage_manifest.v2.schema.json`, every new replay schema, the typed transformer registry and validator implementation are explicitly included in the replay verification implementation inventory and intake seal. Schema/runtime exact-key and adversarial parity are release-blocking tests.

## Atomicity and Windows containment

All origin copies, payload copies, regenerated wrappers, rebase receipts, stage manifests, bridge and review files are built in one exclusive marker-owned sibling staging root. The final run root must be absent. Source/new roots must be distinct and non-nested; all source and destination components are checked against reparse points, ADS, device names, trailing-dot/space aliases, case-fold collisions and traversal.

Files are created exclusively as new regular files, never symlinks/hardlinks/reflinks. Every copy/write is flushed, closed, reopened without following reparses and rehashed. The full staged bridge is validated before same-volume rename-no-replace publishes the final root. On failure, only the owned staging root is removed; run-07 is never changed. Post-publish reopen failure quarantines the new root by no-replace rename rather than leaving a usable partial run.

## Forbidden shortcuts

- No textual/global search-and-replace of run ids or path prefixes.
- No copying a stale wrapper into an operational path and teaching validators to ignore its identity.
- No fresh-looking argv, timestamps or environment for a producer that was not invoked.
- No symlink, junction, hardlink, mount, reflink or external-origin path reference.
- No dereference of any path found in `replay/origin`, old command/execution diagnostics or old comparison/visual wrappers.
- No acceptance of old `run_identity_sha256` in fresh view set, comparison, geometry, visual authority, queue, audit or candidate provenance.
- No partial mapping, unknown-field preservation, lossy semantic projection, caller-defined transformer or generic JSON rewrite.
- No Stage 05/06, decision, allowlist, candidate, promotion or acceptance replay.

## Tests and acceptance criteria

1. **Conservation:** every source Stage 01-04 output row maps exactly once to copied payload or rebased wrapper; missing, duplicate, extra or misclassified rows fail.
2. **Typed transforms:** golden v1-to-replay fixtures for every view state and every Stage 02/03/04 wrapper produce deterministic canonical bytes and fresh seals; unknown/extra/missing fields fail.
3. **Semantic equality:** mutate each comparison block, asset ref, pairwise row, geometry value, packet, image hash/dimension and view inventory row one at a time; even when resealed, projection/recomputation fails.
4. **Absolute-path poisoning:** inject drive, UNC, device, traversal and source-run paths into each Stage 02 diagnostic/receipt, comparison ref/artifact, geometry ref, visual input/layout/command and execution record. Origin hashing remains safe; no operational resolver opens the target; replay fails unless the field is a registered opaque-origin-only field.
5. **Old identity injection:** inject run-07 identity into each fresh view receipt, view set, comparison, geometry, visual manifest, Stage v2 manifest, bridge, queue and Stage 05/06 invocation; every case fails before downstream output.
6. **No fake execution:** replay wrappers contain `producer_invoked=false`; any command/environment/stdout/stderr in a replay execution branch fails schema/runtime validation.
7. **Fresh path resolution:** all returned Stage 03/04/05/06 authorities resolve under the fresh run root to exact bytes/SHA; deleting the source run after successful replay does not break verification or resume.
8. **Two-phase seals:** placeholder, cyclic, self-referential, reordered, post-seal-mutated intake/rebase/stage/bridge graphs fail.
9. **Windows attacks:** reparse, symlink/junction, hardlink, ADS, reserved device, case collision, trailing alias, nested roots and rename collision fail atomically with source unchanged.
10. **Legacy schema authority:** demonstrate run-07 validates through sealed code; mutation of current supplementary v1 schema cannot authorize a malformed legacy manifest. New v2 schema/runtime drift fails.
11. **G1/G2 live closure:** after all code lands, compare actual registry closure hashes, not packet labels. Any changed Stage 01-04 closure member is automatic NO-GO.
12. **Synthetic E2E:** executed synthetic 01-04 -> replay bridge -> fresh queue/decisions -> freshly invoked 05/06. Assert upstream adapters invoked zero times, downstream once, operational stale path count zero, semantic payload equal, and terminal state contains no acceptance claim.
13. **Live run-07:** source receipts remain the four previously sealed identities; operational wrappers carry only the new identity/relative refs; copied payloads retain source bytes; Stage 03/04 validators and direct Stage 05 audit pass their authority preflight without reading run-07; run-07 tree hash/inventory remains unchanged.

## Implementation packets

### HR1 — schemas, projections and registry

Add the replay intake/rebase/bridge schemas; Stage v2 manifest; view execution/view set replay schemas; comparison v3; geometry v2; visual bundle v3; replay command/execution schemas; review queue v2; static exact transformer/projection registry. Tests own schema/runtime parity and every field projection. No live run edits.

### HR2 — authority bridge engine

Implement typed transformers, origin vault, conservation mapping, contained resolver, two-phase sealing and atomic materialization in an additive replay module. Add replay-aware Stage 03/04 validators and the single `validate_replayed_prefix` API. Preserve every Stage 01-04 producer-closure file byte-for-byte; if this proves impossible, stop with NO-GO and require a fresh upstream execution.

### HR3 — downstream adapters and QA

Update only downstream audit/materializer integration plus additive CLI dispatch/tests. Run poisoning, identity-injection, semantic-mutation, Windows atomicity, synthetic E2E and live run-07 eligibility/preflight. A separate independent critic must close P0/P1 before a live fresh run root is created.

## Files checked

- Current Dissociation plan/status, governance boundary and reconstruction skill.
- Packet H architecture and the independent NO-GO critic receipt.
- Run-07 Stage 02 view receipts/view set, Stage 03 comparison, Stage 04 geometry/visual/execution/merge artifacts.
- `kb_creator/pipeline/mineru_cpu_first.py` Stage 02-04 writers and validators.
- `audit_mineru_ai_merge_fidelity.py` and `materialize_mineru_ai_merge.py` fresh authority/path checks.
- Current legacy `stage_manifest.v1` schema identity.

## Verdict

**GO for bounded implementation of the remediated architecture.** The critic P1 is closed at specification level by separating immutable content payloads from run-bound wrappers, preserving old wrappers only as opaque sealed origin evidence, and requiring deterministic typed rebasing plus full semantic conservation under the fresh run identity. **Live replay remains NO-GO** until HR1-HR3 are implemented, the live producer-closure equality proof still passes, and an independent critic closes the implementation. Run-07 remains immutable throughout.
