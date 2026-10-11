# Architect handoff: v2 audit `pass_for_review` contract

Timestamp: `2026-09-15T02:22:36+03:00`

Goal: `20260914-dissociation-publication`

Role: architecture and root-cause analysis, `gpt-5.6-sol` at `high`

Orchestrator policy owner: `gpt-5.6-sol` at `medium`

Assignment state: `platform-unverified`

Scoped override: none for this architecture assignment. The goal-level
engineering override to `gpt-5.6-sol/high` is not transferred to this role.

## Scope

Read-only investigation of the P1 authority mismatch between the canonical
RunSpec v2 Stage 03 comparison producer and the new source-visible completeness
audit. The assigned scope permits this immutable receipt only. No code, run,
decision, `.tools`, canonical plan/context/status, acceptance, publication, Git,
or release artifact was changed.

## Result and verdict

Verdict: **P1 confirmed; minimal generic remediation is specified; Stage 05/06
remain NO-GO until implementation and independent implementation review close
the defect.** This is an architecture verdict, not a release decision.

The producer, JSON Schema, Stage 03 semantic validator, Stage 04 consumer, and
sealed live run all agree that the only successful v2 comparison status is
`pass_for_review`. The v2 completeness audit alone requires the legacy v1
status `pass`. The failure is deterministic contract drift in one predicate,
not a damaged comparison, queue, decision set, provider result, or source run.

## Root cause

`audit_mineru_ai_merge_fidelity.py::audit_v2` at line 398 checks:

```python
comparison.get("status") != "pass"
```

That value belongs to the legacy
`kb_creator.mineru_three_view_comparison.v1` producer at
`compare_mineru_three_views.py:253-287`, specifically line 273. The CPU-first
producer `compare_view_set` emits schema
`kb_creator.mineru_multi_view_comparison.v2` and status `pass_for_review` at
`compare_mineru_three_views.py:306-408`, specifically lines 387-399. Its CLI
also treats only `pass_for_review` as success at lines 411-430.

The defect was not caught by current tests because:

- `test_mineru_cpu_packet_b.py:490-527` proves the v2 producer and schema use
  `pass_for_review`, but its resume path uses `_resume_adapters` at lines
  388-403, which writes a synthetic passing audit and never invokes production
  `audit_v2`;
- `test_audit_mineru_ai_merge_fidelity.py:83-162` exercises the pure
  `audit_v2_content` ledger but does not construct/reopen the complete v2
  run/queue/comparison/decision authority graph through `audit_v2`.

## Canonical comparison producer contract

The authority is the conjunction of the producer, schema, and semantic
revalidator; no consumer may redefine it.

1. Producer: `compare_mineru_three_views.py::compare_view_set`, lines 306-408.
2. Schema: `contracts/mineru_multi_view_comparison.v2.schema.json`, lines 1-18.
   The status enum is exactly `pass_for_review | fail` at line 9; the required
   CPU views are fixed at line 12.
3. Semantic authority: `pipeline/mineru_cpu_first.py::validate_comparison`,
   lines 565-648. An authoritative successful Stage 03 requires all of:
   - exact schema `kb_creator.mineru_multi_view_comparison.v2`;
   - exact status `pass_for_review`;
   - exact run portable identity;
   - exact prepared-manifest and sealed view-set identities;
   - exact required/succeeded/skipped view topology;
   - exact ordered view and pairwise domains;
   - `failures == []`;
   - complete page/layout coverage and recomputed, byte-equivalent view and
     pairwise evidence.
4. Stage output dispatch reuses that validator at
   `mineru_cpu_first.py:651-710`. Every resume reopens it transitively through
   `reconstruction.py::_validate_stage` at lines 1165-1182 and
   `_validate_stage_prefix` at lines 1190-1223.

### Accepted values and meaning

| Comparison schema | Serialized states | State eligible for downstream review | Meaning |
|---|---|---|---|
| `kb_creator.mineru_three_view_comparison.v1` | `pass`, `fail` | `pass` only | Legacy three-view route only. |
| `kb_creator.mineru_multi_view_comparison.v2` | `pass_for_review`, `fail` | `pass_for_review` only, with `failures == []` and the full semantic graph valid | CPU-first evidence is ready for human merge review. It is not reconstruction acceptance or GPU parity. |

For v2, `fail` is a valid failure-document state but is not a successful stage
state: the comparison CLI returns nonzero and the control plane quarantines the
attempt instead of sealing it as authoritative output. Missing, unknown,
case-variant, legacy `pass`, or any v2 status paired with stale/nonempty failure
evidence must fail closed.

## Consumer map

1. `compare_mineru_three_views.py::main`, lines 411-430: producer exit status;
   correctly branches by v1/v2 mode.
2. `mineru_cpu_first.py::validate_comparison`, lines 565-648: canonical v2
   semantic consumer; correctly requires `pass_for_review` and empty failures.
3. `build_mineru_visual_merge_bundle.py::_load_inputs`, lines 302-345: Stage 04
   consumer; correctly requires `pass_for_review` for v2 at lines 312-342 and
   retains legacy `pass` only in the v1 branch at lines 343-344.
4. `reconstruction.py::make_queue`, lines 1226-1293, and `validate_queue`, lines
   1331-1389: seal and reopen the exact comparison path/bytes/SHA. Status
   semantics are supplied by the preceding stage validation, not redefined by
   the queue.
5. `reconstruction.py::production_resume_adapters`, lines 2289-2364: obtains
   only the fixed queue-pinned Stage 03 comparison and supplies it to the v2
   audit. The queue/path/hash logic is correct.
6. `audit_mineru_ai_merge_fidelity.py::audit_v2`, lines 373-444: reopens the
   full run, Stage 01-04, queue, comparison, decision and packet graph. Line 398
   is the sole incorrect status consumer.
7. `materialize_mineru_ai_merge.py::_v2_authority`, lines 199-286: consumes the
   same comparison identity and transitively reruns Stage 03 validation through
   `_validate_stage_prefix`; it does not create a new success vocabulary.
   `_v2_fidelity_authority`, lines 289-346, then requires the exact passing v2
   Stage 05 audit before materialization.
8. `reconstruction_promotion.py` consumes the Stage 05 audit and v2 merge
   provenance identities rather than redefining comparison status. It must
   continue to reject a missing, replaced, legacy, or nonpassing v2 audit.

## Live evidence

Immutable run:
`kb_creator/working/dissociation/reconstruction/20260915-cpu-first-06`.

- comparison SHA-256:
  `85E1D98B47FD7B841E70835325BB89B0752113E2C72535618F2C2B14B2052F16`;
- comparison schema: `kb_creator.mineru_multi_view_comparison.v2`;
- comparison status: `pass_for_review`;
- comparison failures: `[]`;
- required and succeeded CPU views:
  `original_pipeline_txt`, `original_pipeline_ocr`, `raster_pipeline_ocr`;
- run portable identity:
  `AC2A5AD706BA49F7824213BC9BB166A5AC642DD94CDECB89B0717C13CE376429`;
- review queue SHA-256:
  `F11CF0EE2E87A5F1AA9C66899714CCA12A7B48829DFED1E70B590FE175245F57`;
- the queue pins the exact comparison path and the same comparison SHA;
- Stage 03 is sealed `succeeded`, exit `0`, and its stdout reports
  `pass_for_review` with no failures.

Direct read-only canonical validation succeeded:

```text
kb_creator.mineru_multi_view_comparison.v2 pass_for_review []
['original_pipeline_txt', 'original_pipeline_ocr', 'raster_pipeline_ocr']
```

Direct read-only `audit_v2` execution against the run-06 decisions passed all
preceding run/stage/queue checks and then failed exactly at line 398:

```text
ValueError: comparison required CPU authority mismatch
```

This isolates the mismatch to the audit predicate.

## Minimal universal remediation specification

### Runtime change

Change only the v2 status literal in
`kb_creator/scripts/audit_mineru_ai_merge_fidelity.py::audit_v2` line 398 from
`pass` to `pass_for_review`. Preserve the existing checks for exact required
CPU views and run identity. Do not alter `audit_v2_content`, policy thresholds,
allowlist semantics, or legacy `audit` behavior.

The preferred minimal form is a schema-specific closed predicate:

```python
if (
    comparison.get("schema") != "kb_creator.mineru_multi_view_comparison.v2"
    or comparison.get("status") != "pass_for_review"
    or comparison.get("failures") != []
    or comparison.get("required_views") != REQUIRED_CPU_VIEWS
    or comparison.get("run_identity_sha256") != run["portable_identity_sha256"]
):
    raise ValueError("comparison required CPU authority mismatch")
```

The schema and empty-failures checks are defense in depth; canonical
`_validate_stage_prefix` has already enforced the complete producer contract.
If the implementer chooses the absolutely smallest one-token literal change,
it is behaviorally sufficient in the current call graph, but the explicit
schema/failures form better prevents a future refactor from separating the
audit from stage-prefix validation. Do not duplicate the expensive full
comparison recomputation a second time inside `audit_v2`.

### Regression tests

Add production-path coverage, not another pure-ledger-only test.

1. `test_audit_v2_accepts_canonical_pass_for_review_authority`
   - create a complete synthetic CPU-first RunSpec v2 run with existing Packet
     B fixtures;
   - produce Stage 03 through `compare_view_set` so its real status is
     `pass_for_review`;
   - create an exact queue-bound validated decision snapshot;
   - call production `audit_v2`, not only `audit_v2_content`;
   - assert the call reaches content audit and returns a schema-valid v2 report
     (preferably `passed == True` with complete synthetic decisions).
2. Parameterized negative test over `pass`, `PASS_FOR_REVIEW`, `succeeded`,
   missing status, and `fail`:
   - mutate a disposable synthetic comparison and reseal its disposable stage
     manifest/queue as required so the targeted semantic check is exercised;
   - assert production `audit_v2` rejects before emitting a passing report;
   - assert no Stage 05 success output or candidate is created.
3. Preserve a legacy-v1 regression proving schema
   `kb_creator.mineru_three_view_comparison.v1` still accepts only `pass` in
   `legacy-v1` dispatch. The remediation must not change that vocabulary.
4. Add one production-resume integration assertion: with the real resume
   adapter and a canonical `pass_for_review` comparison, Stage 05 must not fail
   with `comparison required CPU authority mismatch`; any deliberately
   incomplete text decision must fail for a content-ledger reason instead.
5. Rerun focused comparison/audit/control/materializer tests and the broader KB
   Creator regression selected by the goal. Test execution must disable or
   contain caches so it does not alter sealed run evidence.

### Acceptance criteria

- Canonical producer output `pass_for_review` passes the authority portion of
  production `audit_v2`.
- V2 `pass`, `fail`, unknown, missing, and case-variant states cannot produce a
  passing Stage 05 report.
- V1 `pass` behavior remains unchanged and cannot enter v2 dispatch.
- Required CPU view order/domain, empty failures, run identity, queue identity,
  fixed run-local paths, reparse containment, decision identities, packet
  projection, and full source-text completeness remain fail-closed.
- No acceptance, GPU parity, or release claim is inferred from
  `pass_for_review`.
- Focused and broad tests pass, then a distinct independent `gpt-5.5/medium`
  implementation review records no P0/P1 before another live run.

## Forbidden shortcuts

- Do not add legacy `pass` to the v2 schema or accept both values for v2.
- Do not change the v2 producer to emit `pass`; that erases the deliberate
  review-only meaning and breaks correct consumers.
- Do not rewrite or reseal run-06 comparison, queue, manifests, decisions, or
  any other immutable run evidence.
- Do not skip Stage 05, downgrade its failure to a warning, or materialize a
  candidate without the exact passing v2 audit.
- Do not add a Dissociation/run-id special case or an external wrapper outside
  the implementation inventory.
- Do not weaken stage-prefix revalidation, queue/path/SHA binding, required CPU
  views, empty failures, or content completeness to make the run advance.

## Run-boundary consequence and next action

`audit_mineru_ai_merge_fidelity.py` is explicitly part of the run
implementation inventory at `reconstruction.py:287-319` (line 316). Therefore
the runtime correction necessarily makes run `20260915-cpu-first-06` stale.
The control plane must reject resume through `_validate_live_run_bindings`;
editing or resealing `-06` would violate immutability.

Next action:

1. bounded engineer implements the generic audit predicate and tests;
2. independent `gpt-5.5/medium` critic reviews the implementation and reruns
   the focused/broad evidence;
3. preserve `-06` as immutable P1 evidence;
4. start a fresh local CPU run (next absent run id, expected `-07`) under the
   corrected inventory;
5. revalidate/copy decisions only through the new run's exact queue,
   comparison, packet and visual identities; then run Stage 05/06 normally.

## Files checked

- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/contracts/dissociation.reconstruction.json`
- `kb_creator/contracts/mineru_multi_view_comparison.v2.schema.json`
- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/pipeline/mineru_cpu_first.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- immutable run-06 Stage 03, Stage 04, review queue, and decision identities.

## Files changed

- Added only this receipt:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_audit_v2_pass_for_review_contract_20260915.md`.

## Verification/evidence

- Repository-wide `rg` inventory of both comparison schemas, status literals,
  fixed Stage 03 path, and consumers.
- Read-only inspection of producer/schema/validator/queue/resume/audit/
  materializer code with exact line numbers.
- SHA-bound inspection of live run-06 comparison and review queue.
- Read-only successful execution of
  `mineru_cpu_first.validate_comparison` against run-06.
- Read-only reproduction of the production `audit_v2` failure at line 398.
- No tests were run because this assignment is a read-only architecture
  investigation and the defect is already isolated by a real sealed run plus
  direct validator/audit execution.

## Blockers

- Runtime P1 at `audit_mineru_ai_merge_fidelity.py:398`.
- Independent implementation closure is required after the code change.
- Run-06 becomes non-resumable after the required inventory change; a fresh
  run is mandatory.

Elapsed time: approximately 14 minutes.

Token use: approximately 10k architecture-agent tokens; exact platform usage
is unavailable.
