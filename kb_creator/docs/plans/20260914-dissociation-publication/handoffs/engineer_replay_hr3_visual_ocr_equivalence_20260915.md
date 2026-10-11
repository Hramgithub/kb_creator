# Engineer receipt — replay HR3 visual/OCR equivalence (Packet I-B)

Date: 2026-09-15  
Role: engineering, `gpt-5.6-sol`, high (user-scoped override)  
Result: **focused implementation PASS; independent closure and broad regression pending**

## Result

- Added a dedicated downstream `python -m kb_creator replay resume` route. It validates the replayed Stage01–04 prefix, creates an immutable run-local decision/allowlist snapshot, executes only Stage05 and Stage06, and returns `candidate_ready_for_reconstruction_qa` without inferring acceptance.
- Added strict v3 content-ledger behavior for positional visual assertions (`before_anchor`, `anchor_prefix`) and same-page, cross-view OCR-equivalence classes with bounded geometry and lexical evidence.
- Added replay-v3 materializer authority/provenance handling bound to the fresh replay bridge, validated submission, fixed Stage03 comparison, and passing Stage05 audit.
- Fixed the downstream inventory exclusion mismatch with a local filtered wrapper; the shared identity helper and the 19-path S1–S4 producer closure were not edited.
- Stage output and manifest publication is paired and staged. A synthetic Stage06 failure leaves neither Stage06 output nor manifest and never creates acceptance evidence.

## Changed files

- `kb_creator/__main__.py`
- `kb_creator/pipeline/reconstruction_replay_resume.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/contracts/validated_reconstruction_submission.v2.schema.json`
- `kb_creator/contracts/replay_downstream_stage_manifest.v1.schema.json`
- `kb_creator/contracts/replay_resume_result.v1.schema.json`
- `kb_creator/contracts/ai_merge_fidelity_reviewed_allowlist.v3.schema.json`
- `kb_creator/contracts/ai_merge_fidelity_audit.v3.schema.json`
- `kb_creator/contracts/mineru_ai_merge_provenance.v3.schema.json`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_reconstruction_replay_resume.py`
- this receipt

No immutable run, decision root, source, `.tools`, canonical plan/status/context, or upstream S1–S4 producer file was changed.

## Focused evidence

Command:

```powershell
$env:PYTHONPATH='.tools/python-test-deps'
<bundled-python> -m pytest -q kb_creator/tests/test_reconstruction_replay_resume.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py
```

Result: **47 passed in 1.62s**.

The focused suite includes:

- full synthetic fresh replay-04 authority graph → immutable decision/allowlist snapshot → real Stage05 v3 content audit → real Stage06 materialization;
- successful validation of the emitted submission, both downstream stage manifests, audit, provenance, and result against the six new Draft 2020-12 schemas;
- three required CPU views with exact-equivalent source-unit coverage;
- positional cover/drop-cap G1 proof-stream cases and placement/anchor/bbox/pair/duplicate attacks;
- G2 OCR-equivalence positive and distance/token/page/selection/bbox/IoU/duplicate/verdict attacks;
- stale bridge, queue, decision, and allowlist identities;
- Stage06 atomic failure and no-acceptance proof;
- dedicated CLI shape and legacy-resume/acceptance call guards.

Additional checks:

- `py_compile`: PASS for the downstream module, CLI, audit, materializer, and focused tests.
- JSON parsing: **6/6** new schemas.
- `jsonschema` Draft 2020-12 schema checks and emitted-instance validation: PASS inside the synthetic E2E.
- scoped `git diff --check`: PASS.

## Risks and pending evidence

- **P0/P1:** none found by the bounded focused suite.
- **P2:** broad replay/materializer/control-plane regression was explicitly not run in Packet I-B and remains pending.
- Independent critic closure remains required before any live replay-resume command.
- The original request's read-only run-07 eligibility and full 19-path hash re-proof were not repeated in this bounded completion; the previously closed HR1/HR2 base is relied on and must be rechecked by closure review.

## Next action

Run an independent critic review, then the bounded relevant broad regression and exact upstream-closure hash comparison. Do not run live replay/resume until both are green.
