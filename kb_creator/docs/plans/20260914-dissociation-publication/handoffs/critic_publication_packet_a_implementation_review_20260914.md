# Independent critic receipt - publication Packet A implementation review

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PAR-publication-packet-a-implementation-review`
- Review kind: `implementation`
- Role: independent critic
- Requested model: `gpt-5.5`
- Requested reasoning effort: `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Participation declaration: I did not implement or materially design Packet A.
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform
  identity unverified
- Assignment state: `platform-unverified`
- Scoped override: none. The recorded engineering override applies only to the
  implementation contributor and does not transfer critic or orchestration
  ownership.
- Scope: read-only implementation review of neutral publication Packet A
  schemas, control-plane skeleton, CLI exposure, and focused tests. I did not
  require Packet B/C production adapters, did not run live Dissociation
  publication, and did not edit implementation or canonical state.
- Changed by this review: added this receipt only.
- Timestamp: `2026-09-14T05:43:34+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:32:00`
- Token use: unavailable

## Files checked

Required canonical and handoff inputs, read in full or targeted full-context
chunks where tool output required splitting:

- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_neutral_publication_architecture_review_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_correction_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_packet_a_20260914.md`

Packet A files checked:

- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/contracts/publication_run_spec.v1.schema.json`
- `kb_creator/contracts/publication_stage_manifest.v1.schema.json`
- `kb_creator/contracts/artifact_acceptance.v1.schema.json`
- `kb_creator/contracts/master_ru_submission.v1.schema.json`
- `kb_creator/contracts/production_package_manifest.v1.schema.json`
- `kb_creator/pipeline/publication.py`
- `kb_creator/__main__.py`
- `kb_creator/pipeline/__init__.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_control_plane.py`

## Verdict

Reject Packet A as authority for downstream Packet B/C or any live publication
run until the P0 and P1 below are fixed and independently re-reviewed.

The implementation is directionally aligned with Packet A's intended scope:
schemas are additive, the publication graph is separate from reconstruction,
the public CLI refuses `publication run`/`resume` before production adapters are
installed, direct HTML-to-PDF builders are not imported by
`kb_creator/pipeline/publication.py`, acceptance is explicit/non-overwriting in
the tested path, and the combined focused suite passes. However, one Stage 50
escape violates the closed P0 correction: a PDF can survive a successful
`docx_candidate` stage outside the checked `artifacts/` and `evidence/`
subtrees, and Stage 60 can then proceed. A second package-verifier gap allows a
manifest to claim `candidate_for_release_review` while semantically declaring
only the Stage 60 manifest.

## Verification performed

Combined suite command:

```powershell
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI'
& 'C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe' -m pytest -q `
  kb_creator\tests\test_pipeline_identity.py `
  kb_creator\tests\test_reconstruction_control_plane.py `
  kb_creator\tests\test_mineru_three_view_tools.py `
  kb_creator\tests\test_mineru_visual_merge_bundle.py `
  kb_creator\tests\test_audit_mineru_ai_merge_fidelity.py `
  kb_creator\tests\test_materialize_mineru_ai_merge.py `
  kb_creator\tests\test_publication_contracts.py `
  kb_creator\tests\test_publication_control_plane.py
```

Result: `100 passed in 18.12s`.

Additional temporary probes were run under OS temp directories only. They did
not modify repository files.

## Evidence

- `kb_creator/__main__.py` exposes nested publication commands. It routes
  `publication preflight`, `record-acceptance`, and `verify-package` to Packet A
  functions, while `publication run` and `publication resume` raise
  `PublicationControlError("Packet A exposes only the synthetic stage engine; production publication adapters are not installed")`
  before using any run root.
- `kb_creator/pipeline/publication.py` defines a fixed ten-stage graph:
  `master_en_candidate`, `master_ru_packets`, `master_ru_candidate`,
  `artview_bundle`, `artview_apply`, `html_candidate`, `docx_candidate`,
  `pdf_candidate`, `production_package`, `offline_verify`.
- The neutral module contains no import or call reference to
  `translator.build_production_pdf`, `build-production-pdf`,
  `build_innsmouth_pdf_from_accepted_html.py`, `build_viral_production.py`, or
  browser/Chromium PDF execution. Its only HTML-renderer token is the stage
  adapter logical name `translator_build_production_html_v1`.
- Contract validation rejects PDF policy terms including `source_html`,
  `engine_command`, `print-to-pdf`, `chromium`, `browser`, and `edge`, and
  requires `word_com_docx_export_v1` with `document_input_role =
  accepted_docx`.
- Preflight returns `ready` without creating the run root in the positive test
  and preserves zero-write behavior on a direct-PDF contract mutation.
- Resume computes an exact manifest prefix, requires per-stage authority inputs,
  validates sealed acceptance/submission/decision records, rejects stale config
  and implementation drift, and materializes one stage per `publication_run` or
  `publication_resume`.
- Stage 50 has explicit checks for PDFs inside `artifacts/`, `evidence/`,
  private residue, and diagnostics; Stage 60 requires exactly one staged PDF and
  diagnostics declaring `document_authority_kind: accepted_docx`, adapter
  `word_com_docx_export_v1`, and `fresh_export: true`.
- The Stage 50 implementation publishes the whole staging directory with
  `staging.replace(output)` after checking only `staging/artifacts` and
  `staging/evidence`; validation of completed stages later recomputes only the
  `outputs` and `evidence` inventory objects, not a closed inventory of the
  entire stage output root.

Temporary probe results:

- A synthetic `docx_candidate` adapter that wrote the primary DOCX and PNG/QA
  evidence plus `staging/leaked-preview.pdf` outside `artifacts/` and
  `evidence/` was accepted. The result was
  `state: awaiting_docx_acceptance`, `completed_stage: docx_candidate`, and the
  leaked file survived as
  `outputs\50-docx-candidate\leaked-preview.pdf`.
- After accepting the DOCX using normal Stage 50 JSON/PNG evidence, Stage 60
  proceeded successfully. The run then contained both
  `outputs\50-docx-candidate\leaked-preview.pdf` and
  `outputs\60-pdf-candidate\artifacts\Sample_RU.pdf`.
- A synthetic package manifest was resealed after reducing
  `stage_manifests` from the original 8 records to only the Stage 60 manifest.
  `verify_production_package()` still returned
  `state: candidate_for_release_review`, `release_state: not_reviewed`,
  `pdf_count: 1`.

## Findings

### P0-1 - Stage 50 retained-PDF escape can succeed and Stage 60 can proceed

Evidence:

- In `kb_creator/pipeline/publication.py`, `_assert_no_stage50_pdf()` checks
  only the two paths passed as `output` and `evidence`; callers pass
  `staging/artifacts` and `staging/evidence`.
- `_invoke_stage()` then publishes the entire `staging` directory with
  `staging.replace(output)`.
- `_validate_stage()` revalidates the manifest `outputs` and `evidence`
  inventories, but not a closed inventory of all files under the published
  stage root.
- The temporary probe demonstrated an accepted successful Stage 50 with a
  retained PDF at `outputs\50-docx-candidate\leaked-preview.pdf`, followed by a
  successful Stage 60.

Why this is P0:

- The architecture correction made "no retained/packageable Stage 50 PDF" a
  success prerequisite. A successful Stage 50 with an unmanifested retained PDF
  directly violates the accepted DOCX-only final PDF boundary and can create
  two PDF byte streams in the same publication run before packaging.

Required remediation:

1. Make each stage output root closed before atomic publication. For Packet A,
   a successful stage directory should contain only the approved top-level
   subtrees, normally `artifacts/` and `evidence/`, and no unmanifested regular
   files or directories.
2. For Stage 50 specifically, recursively scan the entire invocation staging
   root, the would-be output root, and any stage-local private/cache paths for
   `.pdf` suffixes, PDF media kinds, PDF artifact kinds, and bridge path/hash
   diagnostics before writing a successful manifest.
3. Re-run the same recursive Stage 50 no-PDF check during `_validate_stage()` so
   resume/cache cannot proceed across a stale or tampered Stage 50 output.
4. Ensure Stage 50 failure handling does not retain a forbidden bridge/preview
   PDF as a successful output, evidence, cache payload, or package input. If
   quarantine is used for non-PDF partials, the forbidden PDF itself must not be
   retained contrary to the correction receipt.
5. Add a regression where a synthetic Stage 50 adapter writes a PDF at
   `staging/leaked-preview.pdf` outside `artifacts/` and `evidence/`; expected
   result: Stage 50 fails before manifest/output publication, no retained PDF
   remains in output/evidence/cache/package authority, DOCX acceptance is
   impossible, and Stage 60 cannot dispatch.

### P1-1 - Package verifier does not prove complete stage-manifest authority

Evidence:

- `production_package_manifest.v1.schema.json` declares
  `stage_manifests` with `minItems: 8`, not an exact stage set.
- `verify_production_package()` loops over `manifest["stage_manifests"]` and
  requires only that one listed manifest has `stage_name == "pdf_candidate"`.
  It does not require an exact set of stage names, one manifest per required
  package-phase stage, or that the `stage_manifests` list matches the stage
  evidence role semantically.
- The temporary probe removed every `stage_manifests` record except Stage 60,
  resealed the manifest, and verification still returned
  `candidate_for_release_review`.

Risk:

- A package can pass offline verification while its manifest withholds the
  semantic identities of upstream publication stages. That is a false closure
  guarantee for a production candidate, even if the raw files remain in the
  generic inventory.

Required remediation:

1. Decide and encode the exact stage-manifest set required inside a Packet A
   production package candidate. If Stage 70/71 cannot be inside the package
   because they are created after package assembly, state that exclusion
   explicitly and require exactly the completed upstream stage manifests
   expected at package time, including stages 10, 20, 21, 30, 31, 40, 50, and
   60.
2. Enforce exactly one manifest per required stage name in both
   `production_package_manifest.v1.schema.json` where feasible and
   `verify_production_package()`'s standard-library checks.
3. Require acceptance receipt identities in the manifest to exactly match the
   corresponding package roles for MASTER_EN, MASTER_RU, ArtView, HTML, DOCX,
   and PDF; do not rely only on the role files existing.
4. Add negative tests that remove any required stage manifest record, duplicate
   one, substitute the wrong stage name, or omit a required acceptance receipt
   record while keeping the raw file in package inventory; all must fail.

### P2

None.

## Positive checks retained

- No finding is raised for the absence of Packet B/C production adapters. The
  public `publication run`/`resume` CLI rejects before writes, which is the
  correct Packet A behavior.
- No finding is raised for keeping legacy direct HTML-to-PDF routes in the
  repository. Packet A does not import them; existing compatibility code is out
  of scope for this packet.
- No finding is raised for using injected synthetic adapters in tests. That is
  expected for Packet A, provided the skeleton does not make false production
  guarantees.

## Recommendation

Do not authorize Packet A as a valid control-plane foundation for Packet B/C or
live publication yet. Fix P0-1 first, then P1-1, add the specified regressions,
rerun the combined suite, and request a short independent closure review.

This review does not authorize live Dissociation reconstruction/publication,
acceptance recording, production-package promotion, Git operations, or release.

## Next action

Engineer should patch the Stage 50 whole-stage closure/resume validation and
package verifier semantic stage/acceptance closure, then provide a narrow
closure receipt with exact tests and temporary-probe equivalents showing the
two failures no longer reproduce.

## Closure review - Packet A remediation

### Closure metadata

- Closure step id: `4PAR-publication-packet-a-remediation-closure`
- Review kind: `implementation`
- Role: independent critic
- Requested model: `gpt-5.5`
- Requested reasoning effort: `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Participation declaration: I did not implement or materially design the
  remediation under review.
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform
  identity unverified
- Assignment state: `platform-unverified`
- Scoped override: none
- Scope: closure review of the prior Packet A P0-1 and P1-1 findings only,
  plus a check for newly introduced P0/P1/P2 risk. I did not require Packet
  B/C production adapters and did not run live Dissociation publication.
- Timestamp: `2026-09-14T06:04:59+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:34:00`
- Token use: unavailable
- Changed by this closure: appended this section only.

### Files checked

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_publication_packet_a_implementation_review_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_packet_a_remediation_20260914.md`
- `kb_creator/contracts/production_package_manifest.v1.schema.json`
- `kb_creator/pipeline/publication.py`
- `kb_creator/__main__.py`
- `kb_creator/pipeline/__init__.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_control_plane.py`

### Closure verdict

Approve Packet A remediation for downstream Packet A authority, with one
non-blocking P2 schema-tightening follow-up.

The prior P0-1 and P1-1 are closed in the current implementation. Packet A may
proceed as a synthetic control-plane foundation for later Packet B/C work. This
does not authorize live Dissociation publication, production adapters,
acceptance recording, package promotion, Git operations, or release.

### Tests and independent probes

Full suite command:

```powershell
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI'
& 'C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe' -m pytest -q `
  kb_creator\tests\test_pipeline_identity.py `
  kb_creator\tests\test_reconstruction_control_plane.py `
  kb_creator\tests\test_mineru_three_view_tools.py `
  kb_creator\tests\test_mineru_visual_merge_bundle.py `
  kb_creator\tests\test_audit_mineru_ai_merge_fidelity.py `
  kb_creator\tests\test_materialize_mineru_ai_merge.py `
  kb_creator\tests\test_publication_contracts.py `
  kb_creator\tests\test_publication_control_plane.py
```

Result: `107 passed in 36.66s`.

Independent adversarial probes used OS temp directories only and did not modify
repository files:

- Stage 50 nested uppercase stray PDF outside `artifacts/` and `evidence/`:
  blocked with `Stage 50 cannot retain PDF anywhere in its stage scope`; no
  successful Stage 50 output, no Stage 50 manifest, no DOCX acceptance, no
  Stage 60 output, no forbidden PDF residue, and no forbidden JSON bridge
  residue remained.
- Tampered completed Stage 50 with `outputs/50-docx-candidate/nested/STRAY.PDF`:
  both DOCX acceptance and Stage 60 resume were blocked with
  `Stage 50 cannot retain PDF anywhere in its stage scope`; no Stage 60 output
  was created.
- Package verifier mutations after reseal:
  - `only_stage60`: blocked with exact-eight stage-manifest requirement;
  - `missing`: blocked with exact-eight stage-manifest requirement;
  - `extra`: blocked with exact-eight stage-manifest requirement;
  - `duplicate`: blocked with duplicate stage-manifest set detection;
  - `wrong_order`: blocked with packaged stage authority/input mismatch;
  - `wrong_name`: blocked with packaged stage graph/identity mismatch;
  - `missing_acceptance`: blocked with exactly-six acceptance receipt
    requirement.
- Package continuity mutations after reseal:
  - stage tools drift: blocked;
  - stage effective-config drift: blocked;
  - stage implementation identity drift: blocked;
  - upstream chain drift: blocked.

### Closure evidence

- `_assert_no_stage50_pdf()` now scans the whole staging or published Stage 50
  root and stage-local private/cache residue roots; it rejects case-insensitive
  `.pdf` files and PDF/bridge declarations in JSON.
- `_assert_closed_stage_root()` requires each successful stage output root to
  contain exactly `artifacts/` and `evidence/`.
- `_invoke_stage()` applies Stage 50 no-PDF checks before output publication
  and sanitizes forbidden Stage 50 residue on failure before quarantine.
- `_validate_stage()` repeats Stage 50 no-PDF and closed-root checks, so stale
  or tampered Stage 50 outputs cannot authorize later resume.
- `verify_production_package()` now requires exactly eight ordered upstream
  stage manifest records, matching stages 10, 20, 21, 30, 31, 40, 50 and 60.
  Stage 70/71 are excluded as expected because they do not exist when the Stage
  70 package is constructed.
- The package verifier validates each listed stage's stage id, name, version,
  state, upstream chain, input-kind set, adapter identity, cache key, run
  identity, effective config, tools, implementation identity, and shared
  contract/reconstruction authority continuity.
- The package verifier now requires exactly six acceptance receipt identities
  matching the package roles and checks that each receipt binds its packaged
  candidate and producer-stage identity.
- The public CLI still refuses production `publication run` and `publication
  resume` before real adapters exist, so Packet A does not overclaim live
  production capability.

### Findings after remediation

#### P0

None.

#### P1

None.

#### P2-1 - package manifest schema is looser than the verifier for some array cardinalities

Evidence:

- `production_package_manifest.v1.schema.json` now correctly sets
  `stage_manifests` to `minItems: 8` and `maxItems: 8`.
- The same schema still leaves `acceptance_receipts` at `minItems: 6` without
  `maxItems: 6` or `uniqueItems: true`, and `roles` at `minItems: 12` without a
  schema-level max/unique constraint. The runtime verifier is stricter and
  rejects these invalid forms.

Impact:

- No runtime P0/P1 remains because `verify_production_package()` fails closed,
  but standalone schema validation can still accept package manifests that the
  runtime verifier rejects. This is an avoidable schema/code precision mismatch
  in a contract artifact.

Recommended remediation:

- Tighten `production_package_manifest.v1.schema.json` to mirror the verifier:
  `acceptance_receipts` should be exactly six and unique, `stage_manifests`
  should be unique, and `roles` should encode the exact role set/cardinality as
  closely as JSON Schema permits. Add schema-only negative tests for extra
  acceptance receipts and duplicate/extra role declarations.

### Closure recommendation

Packet A may proceed despite P2-1. Close P2-1 before relying on standalone JSON
Schema validation of production package manifests or before release packaging.
Keep Packet B/C, live publication execution, user acceptance recording, stable
promotion, and release review as separate future gates.
