# Architect receipt: RunSpec v2 reconstruction-promotion capability gap

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PF-v2-capability-and-replay-promotion-gap`
- Role: architect / root-cause and remediation specification
- Policy role/model/effort: `gpt-5.6-sol`, `high`
- Actual platform model/effort: unavailable
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: `none` for architecture; the goal's engineering-only Sol/high override remains canonical and unchanged
- Timestamp: `2026-09-15T08:37:00Z`
- Elapsed time: approximately 45 minutes
- Token use: unavailable
- Scope: scenario-neutral promotion of a validated reconstruction RunSpec v2 candidate, including the validated replay-v2 shape used by run09
- Result: root cause and bounded implementation contract complete; no implementation, candidate materialization, acceptance, publication, MinerU execution, commit, or push was performed
- Files changed: this receipt only

## Decision

**GO for bounded implementation of this specification.**

**NO-GO for a one-line deletion or relaxation of the legacy capability check.**
RunSpec v2 replay promotion must dispatch through the already reviewed replay
authorities; it must not be treated as a legacy six-stage run after merely
allowing a missing `run.capability` field.

This decision authorizes implementation and tests only. Live materialization,
reconstruction acceptance, MASTER_EN, publication, and release remain separate
gates.

## Root cause and dependency trace

`reconstruction_promotion._load_run_authority()` successfully loads RunSpec v2,
then unconditionally applies the RunSpec v1 field contract:

```text
run.capability.state == unavailable -> skipped
run.capability.state == injected    -> non-production
run.capability.state != available   -> capability_drift
```

RunSpec v2 deliberately has no `capability`. Its authority graph is:

```text
run_spec.v2
  -> exact ordered view_plan
  -> sealed capability_snapshot/provider receipt
  -> provider_profiles for ready providers
  -> common_tools and local bindings
  -> mandatory pipeline_cpu views
  -> optional provider-local CUDA skips
```

Therefore every valid v2 run currently reaches the third legacy predicate and
fails `capability_drift` before v2 live validation.

For replay-v2 there are additional shape differences which a capability-only
patch would immediately expose:

- authority snapshot is `review/validated-submission-v2/`, not v1;
- Stages 01-04 are typed `stage_manifest.v2` replay manifests;
- Stages 05-06 are `replay_downstream_stage_manifest.v1`;
- Stage 05 audit is fidelity v3;
- Stage 06 candidate root is the flat
  `outputs/06-materialize-candidate/`, not its `candidate/` child;
- Stage 06 provenance is v3 and explicitly carries run, bridge, submission,
  comparison, fidelity, and `acceptance_inferred=false` authority.

The promotion bridge must recognize these existing contracts; it must not
rewrite run09 or manufacture legacy-shaped copies inside its run root.

## Exact support matrix

| Run authority | Promotion support | Capability rule | Chain authority |
|---|---|---|---|
| `run_spec.v1`, profile `mineru_three_view_v1` | Preserve | `available` required; `unavailable` or `skip.json` -> `run_not_promotable_skipped`; `injected` -> `run_not_production_authority` | Existing v1 live binding, validated-submission-v1, stage-manifest v1, fidelity v1, nested candidate |
| Direct executed `run_spec.v2`, profile `mineru_cpu_first_three_view_v1`, no replay marker | Preserve/additive | Required `pipeline_cpu=ready`; optional CUDA may be `ready` or supported `unavailable`; root `skip.json` always blocks | Existing CPU-first live binding, validated-submission-v1, stage-manifest v1, fidelity v2, provenance v2, nested candidate |
| Validated replay `run_spec.v2` with replay markers | Add | Same frozen provider semantics; optional CUDA `unavailable` and its provider-local skipped views are valid | `validate_replayed_prefix`, replay queue/submission validators, exact downstream Stage 05/06 validators, fidelity v3, provenance v3, flat candidate |
| Unknown schema/profile or mixed/partial replay shape | Reject | No fallback | `reconstruction_stage_chain_invalid` before package write |

Replay detection is fail-closed. Presence of **any** replay marker (`replay/`, a
Stage 01-04 v2 manifest, validated-submission-v2, or a replay downstream Stage
05/06 manifest) selects replay-v2 validation. A missing, malformed, or deleted
bridge must not cause fallback to direct-v2 validation.

## Capability semantics

### RunSpec v1

Keep the current behavior exactly. Check `skip.json` first. Then reject
`unavailable`, reject `injected`, and require `available`. Do not make injected
fixtures promotable and do not reinterpret the sealed historical whole-run skip.

### RunSpec v2

Validate the frozen snapshot in fixed provider order:

1. `pipeline_cpu`: `required=true`, `state=ready`,
   `reason_code=verified_cpu_profile`, valid verification receipt, present
   `provider_profiles.pipeline_cpu`.
2. `hybrid_cuda`: `required=false`; either valid `ready` profile or
   `unavailable` with a reason in `OPTIONAL_UNAVAILABLE_REASONS` and no
   verification receipt.
3. `vlm_cuda`: same optional rule.

`invalid`, missing, duplicate, reordered, unknown-provider, unsupported-reason,
or malformed/seal-invalid provider evidence is `capability_drift`. A malformed
RunSpec that lacks the required v2 field itself remains
`reconstruction_stage_chain_invalid` because `load_run()` rejects the data
contract before capability evaluation.

Optional provider-local skipped views do **not** make the run skipped. The exact
view-set validators must still prove that all three required CPU views succeeded
and that a skipped view belongs only to an unavailable optional provider. A
root-level `skip.json` always wins and returns `run_not_promotable_skipped`.

The frozen optional-provider snapshot is authority for that run. A GPU becoming
available later does not invalidate already sealed optional skips. Current
identities of every provider that was `ready` and every common tool must still
match the run bindings.

## Current/live drift authority

### Legacy and direct v2

Continue to use `reconstruction._validate_live_run_bindings()`. Do not weaken
its source, contract, implementation, ready-provider profile, common-tool, or
local-root checks.

### Replay v2

Do not call `_validate_live_run_bindings()` wholesale: a replay run intentionally
has `_replay_inventory()` rather than the direct-run base implementation
inventory. That comparison currently fails even though the stage-scoped replay
authorities are valid.

Promotion must compose these read-only authorities:

1. `reconstruction.load_run()` for the exact v2 shape and portable identity;
2. the existing canonical run-root, contract, source, and local-root checks;
3. frozen provider-snapshot semantics plus current identity validation of all
   ready provider profiles and common tools, using the same MinerU CPU-first
   helpers as the control plane;
4. `reconstruction_replay.validate_replayed_prefix()` for the bridge, registry,
   Stage 01-04 producer closures, conservation mappings, typed references,
   operational inventories, and no-stale-authority proof;
5. `validate_replay_review_queue()` and `load_replay_submission()` for queue,
   bridge, decisions, allowlist, and `acceptance_inferred=false`;
6. `_validate_downstream_stage()` for Stage 05 with `upstream=[]`, then Stage 06
   with exactly the returned Stage 05 record;
7. read-only recomputation with `build_replay_audit()` and exact equality with
   the sealed Stage 05 audit before candidate validation.

This is not an implementation-drift waiver. Replay implementation drift is
checked by the Stage 01-04 producer closures/registry and the Stage 05-06
producer closure. Promotion's own current implementation inventory is bound
into the newly created upstream package and rechecked before acceptance.

## Replay package normalization

Keep the existing four-role `reconstruction-upstream-v1` public package and
separate acceptance contract. Do not add a second acceptance route.

For replay-v2 only:

- consume validated-submission-v2 and normalize its ordered page-decision rows
  for the existing candidate page/decision closure checks;
- validate the flat Stage 06 root, including the exact Stage 06 output inventory,
  page markers/order, contract roles, decision copies, required entities,
  assets, overlay selection, and v3 provenance bindings;
- require v3 provenance `acceptance_inferred=false`, exact fresh run identity,
  bridge SHA, submission identity, comparison identity, fidelity identity, page
  packet/decision identities, and empty unresolved lists;
- generate the existing portable merge-provenance v2 shape from the validated
  v3 provenance plus exact fidelity authorities; do not copy absolute/origin
  paths;
- copy the exact replay intake, bridge, and four rebase receipts under fixed
  `evidence/replay/` paths and include them in package-file closure;
- validate their seals, false acceptance/decision/Stage05-06 replay flags, and
  exact binding to the copied Stage 01-04 manifests;
- retain the existing package stage-record shape. For replay Stage 05/06, the
  package record's digest value is the validated canonical `manifest_sha256`;
  runtime dispatch must validate the actual manifest schema rather than assume
  a v1 `reproducible` body;
- derive the original candidate inventory from the flat Stage 06 output rows;
  legacy/direct-v2 continue stripping the `candidate/` prefix.

Package materialization still ends in
`candidate_awaiting_reconstruction_acceptance`, with no acceptance file.
`record-acceptance` remains the only receipt writer and must rerun the same
run-kind-specific preflight before exclusive creation. No replay artifact,
stage result, candidate status, QA report, or successful command implies user
acceptance.

## Deterministic validation/error order

For both materialize and record-acceptance, use this order; the first failure is
the stable result:

1. malformed/unsupported run contract -> `reconstruction_stage_chain_invalid`;
2. contract/root/local topology failure -> existing `contract_drift` or
   `unsafe_promotion_path`;
3. root `skip.json` or legacy whole-run unavailable ->
   `run_not_promotable_skipped`;
4. legacy injected authority -> `run_not_production_authority`;
5. frozen capability/provider semantic failure -> `capability_drift`;
6. live source/contract/implementation/tool/provider drift -> corresponding
   `source_drift`, `contract_drift`, `implementation_drift`, `tool_drift`, or
   `capability_drift`;
7. replay marker/bridge/stage-chain failure ->
   `reconstruction_stage_chain_invalid`;
8. queue/submission/decision/allowlist failure -> `decision_authority_invalid`;
9. non-equal/non-passing fidelity audit -> `fidelity_not_closed`;
10. candidate/provenance/page/entity/asset failure ->
    `candidate_not_promotable`;
11. existing destination/staging -> `promotion_path_exists`.

Replace substring-only replay error classification with an explicit local map.
Registry or producer-closure drift maps to `implementation_drift`; ready-profile
or common-tool identity drift maps to `tool_drift`; replay graph, seal,
reference, or inventory faults map to `reconstruction_stage_chain_invalid`.

No failure may create `promotion/`, staging residue, an acceptance receipt, or a
success result.

## Minimal engineer file scope

Required changes only:

- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`

No change is required to `reconstruction.py`, `reconstruction_replay.py`,
`reconstruction_replay_resume.py`, CLI arguments, acceptance schemas,
publication code/contracts, scenario contracts/content, run07/run08/run09,
candidate output, plan/context/status, or release state. Reuse the existing
reviewed replay validators rather than modifying their producer closures.

If implementation discovers that the existing upstream-manifest schema cannot
express the normalized stage digest without weakening its current branch, stop
and return for a versioned schema decision; do not silently loosen the schema.

## Exact tests and acceptance criteria

### Positive matrix

1. Existing legacy-v1 materialize/accept/publication-preflight tests remain
   unchanged and pass.
2. Production-shaped direct-v2 fixture with CPU ready and both optional CUDA
   providers unavailable materializes and validates the same four-role package;
   acceptance is absent.
3. Direct-v2 fixture with valid ready optional providers also passes.
4. Synthetic replay-v2 fixture reuses
   `validate_replayed_prefix`, validated-submission-v2 and replay downstream
   stages; materialize creates a package from the flat candidate and no
   acceptance receipt.
5. Reopened replay package validates; a separate explicit acceptance call alone
   creates the exact v1 acceptance receipt; publication preflight then accepts
   the exact inventory/receipt pair read-only.

### Capability and dispatch attacks

6. Parameterize v2 providers: CPU missing/not-ready/skipped, duplicate/reordered
   provider, optional `invalid`, unsupported unavailable reason, unavailable
   provider with receipt, ready provider without profile, snapshot seal mismatch,
   ready-profile drift, and common-tool drift. Assert exact codes above and zero
   promotion writes.
7. Prove valid optional CUDA skipped receipts do not block and prove a skipped
   required CPU view does block.
8. Add `skip.json` beside an otherwise valid v2 run and assert
   `run_not_promotable_skipped` precedes capability/stage errors.
9. Preserve the legacy injected and unavailable tests exactly.
10. Add each partial replay marker independently, including a deleted bridge,
    and assert no direct-v2 fallback.

### Replay authority attacks

11. Mutate/reseal bridge, intake, one rebase receipt, Stage 01-04 seal/output,
    queue bridge, submission seal/page decision/allowlist, Stage 05/06 bridge or
    upstream, fidelity v3 authority/policy/completeness, and provenance v3
    run/bridge/submission/comparison/fidelity/packet identity. Each fails at the
    specified class before writes.
12. Set any `acceptance_inferred`, `decisions_replayed`, or
    `stages_05_06_replayed` flag true and assert rejection.
13. Assert the candidate root branch is exact: nested-only direct candidate is
    not accepted as replay, flat-only replay candidate is not accepted as
    direct, and extra files fail package closure.
14. Assert materialize and preflight never call MinerU, replay execution, Stage
    05/06 producers, or any acceptance writer.

### Real run09 read-only gate

15. Add a repository-conditional test (skip only when the immutable fixture is
    absent) that invokes the factored **read-only** promotion preflight on
    `20260915-cpu-replay-09`. It must prove:
    `run_spec.v2`, `pipeline_cpu=ready`, both optional CUDA providers
    `unavailable/nvidia_device_not_detected`, valid replay prefix/queue/
    submission/Stage05/Stage06, exact recomputed fidelity v3, promotable flat
    candidate, and no `promotion/` before or after. It must not invoke MinerU.

Current read-only evidence supports this test: run09 `load_run` passes; replay
prefix, review queue, validated submission, Stage 05, and Stage 06 validators
pass; fidelity v3 recomputation equals the stored audit; the CPU provider
profile and common-tool identities match. The current generic live-binding call
fails only because it compares replay inventory with direct-run inventory, which
is the dispatch defect specified above.

Acceptance criteria are: all three supported matrix rows pass; all mixed or
malformed rows fail with deterministic codes; existing v1 safeguards remain;
optional GPU skips do not block required CPU promotion; replay evidence is
portable and package-closed; preflight is read-only; materialize creates no
acceptance; and an independent implementation critic closes P0/P1 before any
live run09 materialization.

## Findings

### P0

None found.

### P1

1. Unconditional v1 `run.capability` evaluation blocks every valid RunSpec v2.
2. Capability-only relaxation would still misroute validated replay-v2 through
   v1 submission, stage, audit, candidate, and package assumptions.
3. Whole-run direct implementation validation is not the replay authority and
   rejects the valid stage-scoped replay inventory; promotion must compose the
   closed replay validators instead.

### P2

1. Current substring-based drift classification is not deterministic enough for
   replay reason codes; use the explicit local map above.
2. Canonical plan/context/status still name replay-08 as current while the
   assigned observed authority is replay-09. Only the orchestrator may reconcile
   canonical state after implementation/review; this receipt does not edit it.

## Files checked and verification evidence

Checked the repository instructions and governance, KB Creator README/status,
active Dissociation plan/context, prior promotion architecture/engineering/QA/
critic/schema-parity receipts, replay authority bridge receipts,
`reconstruction_promotion.py`, reconstruction CPU-first live binding logic,
RunSpec v1/v2 and provider-capability schemas, replay/replay-resume validators,
promotion/control/replay tests, and immutable run07/run08/run09 authority shapes.

Read-only run09 probes performed with Python `-B` only, no MinerU subprocess:

- `load_run`: pass (`kb_creator.run_spec.v2`);
- replay prefix: pass, bridge
  `F2BF64CA2D6E2A955A8B81A19C346A6B60C208CD99271FE8E1B4201D60E65C9D`;
- replay queue, validated submission, Stage 05 and Stage 06: pass;
- recomputed fidelity v3 equals stored audit: true, six pages, zero errors;
- current ready CPU profile/local profile/common-tool bindings: all match;
- no `skip.json`; no `promotion/`; both optional CUDA providers are valid
  provider-local unavailable records.

No test suite, MinerU/CPU extraction, materialization, acceptance, source/run
mutation, canonical-state edit, commit, or push was performed.

## Blockers and next action

Blockers: implementation and independent implementation review are pending.
Explicit user reconstruction acceptance remains absent and must not be inferred.

Next action: assign the bounded engineer to the three files above, run the exact
matrix including real run09 read-only preflight, then obtain independent
implementation review. Only after P0/P1 closure may the orchestrator decide
whether to invoke live run09 `materialize`; it must stop again before any
acceptance command.

## Final GO / NO-GO

- Bounded generic implementation: **GO**.
- Capability-only patch: **NO-GO**.
- Live run09 materialization: **NO-GO pending implementation tests and independent review**.
- Acceptance, MASTER_EN, publication, or release inference: **NO-GO**.
