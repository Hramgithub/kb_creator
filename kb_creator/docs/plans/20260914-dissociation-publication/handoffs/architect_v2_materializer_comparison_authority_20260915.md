# Architecture receipt: v2 materializer comparison authority

## Receipt metadata

- Goal id: `20260914-dissociation-publication`.
- Step id: `4-v2-materializer-comparison-authority-spec`.
- Role: architect; root-cause analysis, dependency tracing, and remediation
  specification only.
- Requested policy model/effort: `gpt-5.6-sol`, `high`.
- Actual platform model/effort: unavailable; repository-policy assignment only.
- Assignment state: `platform-unverified`.
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; this contributor does
  not own or change orchestration.
- Scoped override: none for the architect role. The goal's existing engineering
  override does not apply to this architecture assignment.
- Timestamp: `2026-09-15T00:11:56+03:00` (`Europe/Moscow`).
- Elapsed time: approximately `00:32:00`.
- Token use: unavailable.

## Scope and result

Read-only diagnosis is complete. The defect is a reusable Stage 06 authority
wiring gap, not a defect in the six reviewed page decisions and not a missing
MinerU view. The v2 control plane seals its comparison at
`outputs/03-compare-views/comparison.json`, but the production materializer is
given no comparison argument and unconditionally reads the legacy standalone
location `<raw-root>/comparison/comparison.json` below Stage 02.

Decision:

- **GO** for the bounded, scenario-neutral implementation specified below,
  followed by focused QA and an independent `gpt-5.5` implementation review.
- **NO-GO** for resuming or modifying
  `20260914-cpu-first-04` after that implementation changes. The run pins the
  current `reconstruction.py` and materializer identities; a correct code fix
  must make ordinary resume reject that run as `stale implementation`.
- **NO-GO** for a manual comparison copy, junction, symlink, reparse alias,
  monkeypatch, disposable-mirror promotion, run-manifest rewrite, or relaxed
  implementation check.
- After implementation and independent closure, use a fresh absent run root
  with run id `20260915-cpu-first-05`. The old `-04` run remains immutable
  successful `needs_review`/decision evidence, not a resumable candidate.

No live run/resume, network, GPU, remote/API, source, decision, candidate,
acceptance, publication, Git, canonical plan/context/status, or release action
was performed. Only this receipt was added.

## Exact evidence and earliest failing layer

### Real v2 run evidence

- Run root:
  `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-04`.
- Run schema/profile:
  `kb_creator.run_spec.v2` / `mineru_cpu_first_three_view_v1`.
- Run identity:
  `D6370C968BD209E82F8DB6E9511187ED0EB0426E8EE1F48E35A267C6E683105F`.
- Source identity: `2,159,317` bytes, SHA-256
  `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B`,
  six pages.
- Stage 02 sealed the required succeeded view order
  `original_pipeline_txt`, `original_pipeline_ocr`,
  `raster_pipeline_ocr`; optional CUDA views are explicit skips.
- Stage 03 comparison exists at
  `outputs/03-compare-views/comparison.json`: `449,244` bytes, SHA-256
  `C76C2F43B7027207A1CE01490A0D5BC0A2EA5B0F2EC6D6B5EBCB88A35282DA26`,
  schema `kb_creator.mineru_multi_view_comparison.v2`, state
  `pass_for_review`, failures `[]`.
- The legacy path
  `outputs/02-mineru-three-view/comparison/comparison.json` does not exist.
- Stage 04 `visual/visual_manifest.json`, its sealed geometry plan, and the
  sealed review queue all bind the same Stage 03 SHA-256 above. The geometry
  plan additionally binds the exact Stage 02 view-set identity and receipt
  seal.
- Stage 01-04 reproducible manifest identities are respectively
  `91DA7D7C0D0FB421A30BF926130CB5A3C2264DBD4C9B11F3710D63CF953E164A`,
  `A243877571CE5B82921411109CB01C6B22C08E68A613C67D7DA0A4C12C85A6FE`,
  `C583C90552534B7AE771B12288EF7362A6F55C49E58D15FAD761270DEE3F71FC`,
  and
  `E862AD15D4759B41D9E407B63BC579111EAF1417EDD8A98994764D6C7C52B795`;
  the queue seal is
  `9473637F2F866385C6D6DE23AADA302E970A6D69BB32EDAC6B82A7A5F115D2C4`.
- All six sibling page decisions use
  `kb_creator.mineru_ai_page_decision.v1`, cover pages 1-6 exactly, have
  `unresolved: []`, and have `review.visual_reviewed: true`. Their SHA-256
  values in page order are
  `147B2397D2DD594F0E4863AD6AB71E1F4A83DD7521124C78D47D129187A46E5C`,
  `3E1CA05990CC2209DC1EC11BA5EC055E58C603020DD175816FB48D6499B8FEA6`,
  `D18EC8A9671CE0D3D51705C79168828CE8CE389A822EBB3BE2B78AC9EFFCB5D8`,
  `0FE860EC46EB08059376629266726FC529D0463B3AF745C4589F89CCA0FB535E`,
  `0455DC00336AC4EB3CCDAE11A6E6ABDFB304C3711CFFECA8E8C6EC229071D958`,
  and
  `8DB9CAEB866CA2C4D11FCB37884421E1D29FC6E9AD1C2C0C706EE201274801B6`.

### Code-path evidence

The fixed graph is:

```text
Stage 02 raw views + view-set
  -> Stage 03 sealed multi-view comparison
  -> Stage 04 sealed bundle/packets/geometry + sealed review queue
  -> closed decision set and validated submission snapshot
  -> Stage 05 fidelity audit over Stage 04 merge packets
  -> Stage 06 materializer over Stage 04 packets + Stage 02 raw assets
                             + Stage 03 comparison
```

`production_resume_adapters()` currently wires Stage 05 correctly to the
Stage 04 `merge_packets` root containing `merge_index.json`. It wires Stage 06
only with `--bundle-root`, `--raw-root`, `--decisions-root`, and
`--output-root`. It drops the Stage 03 comparison path and identity.

`materialize_mineru_ai_merge._load_bundle(bundle_root, raw_root)` then sets:

```text
comparison_path = raw_root / "comparison" / "comparison.json"
```

The later `MERGE_PROVENANCE.json` repeats the same derived legacy path. The
earliest failing layer is therefore the production Stage 06 adapter/CLI data
contract. Stage 05, the reviewed decisions, Stage 03 comparison, Stage 04
packets, and raw view artifacts are upstream dependencies, not the cause.

The current focused baseline remains green despite the production defect:

```text
test_materialize_mineru_ai_merge.py + test_reconstruction_control_plane.py
48 passed in 6.44s
```

Those tests use a synthetic legacy tree with
`raw/comparison/comparison.json`, and the only production resume argv
regression checks Stage 05. There is no v2 Stage 06 argv or Stage03-path test.

### Immutable implementation consequence

The `-04` RunSpec pins the current files exactly:

- `kb_creator/pipeline/reconstruction.py`:
  `455FCD32C1369F7E6381886EF8C73AA23CF861520F3F776E265205E0E29108D3`;
- `kb_creator/scripts/materialize_mineru_ai_merge.py`:
  `8A9AB05F80AB1F72B458573371392D64A08B176DE737096385EBEE74AADABE90`.

Both match the files at inspection time. `_validate_live_cpu_first_bindings()`
requires the complete current implementation inventory to equal the RunSpec
inventory before resume and before each stage. Editing either file correctly
invalidates `-04`. This is an intended fail-closed property and must not be
bypassed or supplemented for this defect.

## Remediation contract

### 1. Queue is the Stage 03 locator authority

Strengthen `validate_queue(path, run)` before any decision snapshot or output
write. Its existing sealed `comparison` record must be a closed object with
exactly `path`, `bytes`, and `sha256` and must satisfy all of the following:

1. `path` is the canonical forward-slash run-relative literal
   `outputs/03-compare-views/comparison.json` for the fixed graph.
2. The path is non-absolute, contains no `..`, empty or dot component,
   backslash, colon/ADS form, or alternate normalization.
3. Resolving it below the exact RunSpec-bound run root remains inside that root
   and lands on the Stage 03 comparison file.
4. No existing component is a symlink, junction, mount/reparse point, or other
   alias accepted by the repository containment helper.
5. The actual `{bytes, sha256}` equals the sealed queue record.
6. For RunSpec v2 it also equals the comparison identity already proven by the
   validated Stage 03 output, Stage 04 visual manifest, and Stage 04 geometry
   plan. Divergence fails before Stage 05 exists.

Do not derive a new authority by hashing an arbitrary caller path. The sealed
queue record is the locator/identity authority; the filesystem is only checked
against it.

### 2. Explicit production Stage 06 argv

Pass the already validated queue comparison record into
`production_resume_adapters()` (or an equivalently narrow immutable value
object). For the v2 production route, append exactly once:

```text
--comparison <resolved contained Stage03 path>
--comparison-sha256 <sealed queue SHA-256>
```

The adapter must not use `sha256_file(comparison)` as the expected identity,
because that would bless whichever bytes happen to be present at invocation
time. It may re-hash only to compare with the sealed expected digest.

Stage 05 keeps its current argv and merge-index-root contract. Both resume
stages remain bound to the same validated submission snapshot. Their cache
identity already includes, without adding a second authority format:

- the Stage 03 and Stage 04 upstream manifest receipts;
- the decision-set/page/allowlist identities;
- the decision set's sealed `review_queue_sha256` binding;
- the run implementation inventory and adapter script identities.

The implementation tests must prove that comparison, queue, packet, decision,
or implementation drift changes or invalidates this graph before a candidate
can succeed. Do not introduce an unsealed side-channel argument, manual
manifest, or absolute-path-only cache key.

### 3. Materializer CLI/API compatibility branch

Extend the reusable API with optional keyword-only comparison authority and
the CLI with an all-or-none pair:

```text
--comparison <path>
--comparison-sha256 <64 uppercase/lowercase hex accepted, normalized for compare>
```

Contract branches:

- **v2 visual bundle:** both values are mandatory. Omission of either or both
  fails before output creation, even if a file has been planted at the legacy
  Stage 02 location.
- **legacy v1/standalone bundle:** omission of both preserves the existing
  `raw_root/comparison/comparison.json` behavior and all existing call sites.
  Supplying only one always fails. No existing legacy fixture is rewritten.
- A v2 comparison must never be accepted through the legacy fallback. Bundle
  schema/manifest inspection selects the branch, not existence of a convenient
  file and not a scenario name.

The materializer must carry the selected comparison path through its call
stack and write that exact resolved path into the existing `raw_comparison`
field. Do not add fields to `kb_creator.mineru_ai_merge_provenance.v1` in this
bounded patch; the promotion bridge currently enforces its exact key set.

### 4. V2 cross-binding and containment checks

Before page decisions or raw assets are validated, the v2 branch must prove:

1. the explicit comparison is a regular non-reparse file under the same
   RunSpec-bound run root and at the fixed Stage 03 topology;
2. its actual bytes/hash equal the sealed queue authority supplied by the
   adapter;
3. the sealed Stage 04 v2 visual manifest binds the same comparison path/hash
   and the exact `raw_root`/view-set path;
4. the sealed Stage 04 geometry plan binds the same comparison bytes/hash,
   run identity, exact Stage 02 view-set bytes/hash/receipt seal, succeeded view
   order, and required CPU triptych prefix;
5. the comparison has schema `kb_creator.mineru_multi_view_comparison.v2`,
   state `pass_for_review`, no failures, the same run identity, and the exact
   Stage 02 sealed view-set identity/receipt;
6. comparison `succeeded_views`, comparison `views` order, geometry-plan order,
   and view-set `succeeded_views` agree exactly.

Reuse existing v2 bundle/view-set/seal validators where their contracts match;
do not duplicate a weaker partial validator. All paths used for reads must pass
containment and non-reparse checks before the read. All checks occur before
`output_root.parent.mkdir()` or staging creation. Existing atomic staging,
non-empty-output refusal, raw-asset containment, and failure quarantine remain
unchanged.

### 5. Fresh-run and decision handling

After bounded implementation and independent closure:

1. leave `20260914-cpu-first-04` and its sibling decisions byte-for-byte
   unchanged;
2. start only fresh absent run id `20260915-cpu-first-05` through the normal
   production control plane;
3. require Stage 01-04 to regenerate and seal under the new implementation
   inventory; do not import Stage 03/04 files from `-04`;
4. a fresh decision-set manifest is mandatory because it must bind the new
   queue seal and run authority;
5. existing page-decision bytes may be reused only after an automated exact
   per-page comparison proves the fresh Stage 04 packet identity and queue-item
   semantics expected by each decision. Any changed packet, view/raw-index,
   role, issue domain, or visual evidence requires revalidation/re-authoring;
6. never copy or infer reconstruction acceptance from `-04`. Successful Stage
   06 still means only `candidate_ready_for_reconstruction_qa`.

## Bounded implementation ownership

Allowed code/test changes:

- `kb_creator/pipeline/reconstruction.py`:
  validate the sealed queue comparison locator/identity, carry it to the
  production resume adapter, and construct the v2 Stage 06 argv.
- `kb_creator/scripts/materialize_mineru_ai_merge.py`:
  add the explicit pair, v2/legacy branch, cross-binding/containment checks,
  and correct `raw_comparison` provenance path.
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`:
  legacy parity plus v2 positive/adversarial materializer coverage.
- `kb_creator/tests/test_reconstruction_control_plane.py`:
  queue validation and exact production Stage 06 argv coverage.
- `kb_creator/tests/test_mineru_cpu_packet_b.py`:
  one scenario-neutral synthetic v2 run/review/resume regression and drift
  cases using existing fixture infrastructure.
- `kb_creator/tests/test_reconstruction_promotion.py` only if an assertion is
  needed to prove the unchanged provenance/promotion contract; production
  promotion behavior is not otherwise owned.

No scenario contract, source/runtime/model, immutable run, page decision,
publication adapter, promotion schema, acceptance/release record, README,
canonical goal state, or scenario-specific executable is in scope. No new
schema is required if the existing exact-key runtime contracts and transitive
stage/cache bindings are retained. If implementation discovers that a schema
must change, stop and return a narrower schema delta for architecture review
instead of silently expanding this packet.

## Required acceptance tests

The bounded implementation is not review-ready until all of these pass:

1. V2 positive: Stage02 has no comparison child; explicit sealed Stage03
   comparison materializes a synthetic candidate and provenance names Stage03.
2. V2 omission: zero or one comparison argument fails before any output or
   staging path is created.
3. Legacy positive: the unchanged standalone v1 fixture with
   `raw/comparison/comparison.json` and no new flags produces byte-compatible
   outputs for the established assertions.
4. Authority drift: wrong bytes, SHA, queue record, Stage03 manifest identity,
   Stage04 visual-manifest identity, or geometry-plan identity fails closed.
5. View graph drift: wrong run identity, view-set hash/receipt seal, required
   CPU triptych, succeeded-view order, comparison view order, skipped/succeeded
   state, or non-empty comparison failures fails closed.
6. Path attacks: absolute outside-root path, traversal, backslash/UNC, ADS,
   normalized alias, Stage02 planted copy, symlink, junction/reparse component,
   and same-byte outside-root file are rejected before output.
7. Exact argv: production v2 Stage06 contains one `--comparison` and one
   `--comparison-sha256` sourced from the validated queue; Stage05 still points
   at the merge-index root; legacy dispatch remains compatible.
8. Resume/cache: queue, comparison, packet, decision, allowlist,
   source/contract/tool, or implementation mutation is rejected before an
   accepted candidate; Stage05/06 manifests retain exact ordered upstream and
   decision inputs.
9. Atomicity: every authority failure leaves candidate absent, preserves any
   pre-existing non-empty output, and does not create a succeeded Stage06
   manifest.
10. Promotion parity: `MERGE_PROVENANCE.json` keeps the exact v1 key set and
    promotion validation remains green.
11. Full focused suites:
    `test_materialize_mineru_ai_merge.py`,
    `test_reconstruction_control_plane.py`,
    `test_mineru_cpu_packet_b.py`,
    `test_reconstruction_promotion.py`, and
    `test_reconstruction_promotion_adversarial.py`; plus `py_compile` and
    `git diff --check` for the owned files.
12. Static scenario-neutrality: no new `Dissociation`, Viral/Innsmouth page
    count/range, run id, device path, network/API/remote path, manual copy, or
    acceptance shortcut in reusable code.

## Risks and controls

- **Fresh-run cost:** implementation identity invalidates `-04`. This is
  intentional; run `-05` is the only allowed production continuation.
- **False legacy fallback:** a copied Stage03 file under Stage02 could hide the
  defect. V2 bundle detection must require explicit authority regardless of
  file existence.
- **Fresh-hash blessing:** computing the expected digest from the supplied
  file would erase the sealed authority. The queue digest is authoritative.
- **TOCTOU:** validate identity again in the materializer immediately before
  parsing; cross-check the sealed bundle graph before any write. Existing
  stage inventory checks remain the outer defense.
- **Absolute paths in historical JSON:** v2 manifests contain local absolute
  locators. They are evidence only after equality to contained, RunSpec-derived
  paths; they are never used directly as writable targets.
- **Decision carryover:** page JSON does not itself bind the fresh queue.
  Require a new decision set and exact packet/queue revalidation; never infer
  acceptance.
- **Promotion breakage:** adding provenance fields would fail its exact-key
  validator. Keep the schema shape unchanged and only correct the existing
  path value.

## Assumptions

- The fixed reconstruction graph continues to place v2 Stage02, Stage03, and
  Stage04 under one RunSpec-bound `outputs/` root.
- `validate_v2_bundle`, view-set sealing, stage inventories, queue sealing, and
  validated submission snapshots remain the canonical reusable validators.
- Legacy direct materializer callers still rely on the two-argument
  bundle/raw topology and are covered by current synthetic tests.
- An independent critic reviews the implementation before any fresh real run.

## Blockers and next action

Architecture blocker: none for the bounded fix.

Execution blocker: `20260914-cpu-first-04` cannot be resumed after the fix
without violating its immutable implementation binding. This is resolved by
the required fresh-run branch, not by weakening validation.

Next action: assign the bounded files above to engineering, require the complete
synthetic/adversarial evidence, then obtain an independent `gpt-5.5`
implementation closure. Only after that closure may the orchestrator start
fresh absent run `20260915-cpu-first-05`. No release decision is made here.

## Files checked or changed

Checked:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md` active-goal section
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/mineru_cpu_first.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/contracts/run_spec.v2.schema.json`
- `kb_creator/contracts/stage_manifest.v1.schema.json`
- `kb_creator/contracts/reconstruction_decision_set.v1.schema.json`
- `kb_creator/contracts/mineru_multi_view_comparison.v2.schema.json`
- `kb_creator/contracts/mineru_view_set.v1.schema.json`
- `kb_creator/contracts/mineru_visual_merge_bundle.v2.schema.json`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- immutable run structures for `20260914-cpu-first-03` and
  `20260914-cpu-first-04`
- sibling decision files under `20260914-cpu-first-04-decisions/pages`

Changed:

- added this immutable receipt only:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_v2_materializer_comparison_authority_20260915.md`

No canonical plan, context, project status, release file, source, decision,
code, schema, test, run, candidate, publication artifact, or Git state was
changed by this assignment.
