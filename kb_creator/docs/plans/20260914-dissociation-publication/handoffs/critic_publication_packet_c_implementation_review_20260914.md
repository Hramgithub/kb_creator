# Independent critic receipt - Packet C implementation review

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PC-implementation-review`
- Review kind: `implementation`
- Reviewer role: independent critic, requested `gpt-5.5` / `medium`
- Platform identity: unavailable; role assignment state `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`; ownership not transferred
- Scoped override: none for critic role
- Timestamp: `2026-09-14T11:34:48+03:00`
- Elapsed time: unavailable in-receipt; final goal tool report should be treated
  as authoritative
- Token use: unavailable in-receipt; final goal tool report should be treated
  as authoritative
- Participation declaration: I did not implement or materially design Packet C.
  I reviewed current worktree code, schemas, tests, receipts, and synthetic
  adversarial behavior only.
- Candidate state reviewed: non-frozen implementation candidate; no live
  Dissociation run, user acceptance, release, Git, or canonical plan/context
  mutation authorized.

## Files checked

- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_correction_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_publication_packet_a_implementation_review_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_publication_packet_b_implementation_review_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_packet_c_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_packet_c_completion_20260914.md`
- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/contracts/publication_run_spec.v1.schema.json`
- `kb_creator/contracts/publication_stage_manifest.v1.schema.json`
- `kb_creator/contracts/production_package_manifest.v1.schema.json`
- `kb_creator/pipeline/publication.py`
- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/pipeline/__init__.py`
- `kb_creator/__main__.py`
- `kb_creator/scripts/production_docx.py`
- `kb_creator/scripts/export_docx_to_pdf.ps1`
- `kb_creator/scripts/publication_render_qa.py`
- `kb_creator/scripts/verify_production_package.py`
- `kb_creator/scripts/scenario_artview.py`
- `kb_creator/scripts/scenario_artview_apply.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_control_plane.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- `kb_creator/tests/test_publication_docx_adapter.py`
- `kb_creator/tests/test_publication_docx_to_pdf.py`
- `kb_creator/tests/test_publication_render_qa.py`
- `kb_creator/tests/test_production_package_verifier.py`
- `kb_creator/tests/test_production_docx.py`
- `kb_creator/tests/test_publication_registry_e2e.py`
- `kb_creator/tests/test_scenario_artview_v3.py`
- `kb_creator/tests/test_scenario_artview.py`
- Document/PDF workflow skill constraints were checked for the relevant
  DOCX-render and PDF-render expectations.

## Verdict

Approve Packet C implementation for the next bounded orchestration step.

No P0 or P1 findings remain in the reviewed scope. The fixed production
registry is present, public run/resume use the fixed registry, one invocation
advances at most one stage, and the control plane still requires explicit user
acceptance gates. Stage 40 has no direct PDF callable; Stage 50 is DOCX plus
PNG/JSON evidence only and fail-closes on retained PDF/private bridge residue;
Stage 60 uses exact accepted DOCX authority and fresh Word COM PDF export with
repository Poppler render QA; Stage 70 packages the required ArtView/config/code
schema evidence and exactly one Stage 60 PDF; Stage 71 executes the copied
offline verifier with `python -I` and returns only a non-release verification
result.

This approval is not release approval and does not authorize live Dissociation
publication, acceptance recording, production package promotion, Git mutation,
or a final release decision.

## Evidence

### Focused suite

Command:

```text
PYTHONPATH=C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI
C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe -m pytest -q kb_creator\tests\test_publication_contracts.py kb_creator\tests\test_publication_control_plane.py kb_creator\tests\test_scenario_master_ru.py kb_creator\tests\test_scenario_artview_v3.py kb_creator\tests\test_publication_html_adapter.py kb_creator\tests\test_publication_docx_adapter.py kb_creator\tests\test_publication_docx_to_pdf.py kb_creator\tests\test_publication_render_qa.py kb_creator\tests\test_production_package_verifier.py kb_creator\tests\test_production_docx.py kb_creator\tests\test_publication_registry_e2e.py
```

Result:

```text
56 passed, 2 skipped, 14 subtests passed in 130.88s (0:02:10)
```

The skips are acceptable host-condition evidence, not success claims: Windows
did not permit the symlink/reparse adversarial fixture, and Word COM activation
is unavailable in this Codex logon with `0x80070520`. The latter is correctly
classified as no successful live Word export evidence.

### Legacy/v2 parity

Command:

```text
PYTHONPATH=C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI
C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe -m pytest -q kb_creator\tests\test_scenario_artview.py --deselect kb_creator/tests/test_scenario_artview.py::ScenarioArtViewTests::test_real_viral_bundle_contract_and_decision_validation
```

Result:

```text
9 passed, 1 deselected in 0.22s
```

The deselected test is the known unavailable generated Viral fixture, not a
Packet C regression.

### Static checks

- Python compile:

```text
py_compile passed for publication.py, publication_adapters.py, __main__.py,
production_docx.py, publication_render_qa.py, verify_production_package.py,
scenario_artview.py, and scenario_artview_apply.py.
```

- PowerShell AST parse:

```text
PowerShell AST parse: pass
```

### Independent adversarial probes

All probes used temporary synthetic roots under `C:\_Hobby\_work\NRI\tmp` and
did not mutate product code or canonical project state.

Observed results:

```text
direct_route_config_rejected_zero_write -> PublicationControlError: PDF authority must be exact accepted DOCX through Word COM
cli_invalid_runtime_no_write -> exit=2 run_root_absent=True
stage50_pdf_private_json_residue_rejected -> PublicationControlError: publication stage docx_candidate failed: Stage 50 private bridge or cache residue blocks success
stage60_supplied_pdf_rejected_no_write -> PublicationControlError: pdf_candidate requires exactly: ['docx_acceptance']
package_extra_pdf_rejected -> PublicationControlError: production package inventory mismatch
package_missing_acceptance_rejected_after_reseal -> PublicationControlError: package must contain exactly six acceptance receipt identities
copied_verifier_isolated_cwd_py_path -> exit=0 state=candidate_for_release_review
```

The Stage 50 probe also verified no `50-docx-candidate` output, no stage
manifest, no Stage 60 output, no private bridge root, no quarantined PDF, and
no quarantined bridge-diagnostic JSON remained after failure handling.

## Findings

### P0

None.

### P1

None.

### P2-1 - JSON Schemas remain looser than runtime for several exact Packet C invariants

Evidence:

- `scenario_publication_contract.v1.schema.json` allows generic `render_profile`
  adapter strings for `html` and `docx`; runtime `_validate_contract()` narrows
  them to `translator_build_production_html_v1` and
  `production_docx_explicit_config_v1`.
- `scenario_publication_contract.v1.schema.json` allows package
  `required_roles` with `minItems: 12`; runtime requires all mandatory package
  roles by subset check.
- `publication_stage_manifest.v1.schema.json` leaves `tools` items as generic
  objects; runtime `_registry_tools()` requires closed `name/version/scope`
  records and rejects mixed injected/production identities.

Impact:

Runtime behavior is fail-closed and the focused tests/probes confirm the safety
boundary. The gap is non-blocking for bounded implementation review, but it is
not ideal for treating the JSON Schemas as exact standalone contracts before a
frozen production-package or release review.

Remediation:

Before release packaging or external schema publication, tighten the schemas to
match the accepted runtime invariants: split `html` and `docx` render-profile
definitions or add context-specific adapter constants; set package
`required_roles` to exact cardinality/role set; and define closed production
tool records with the allowed scopes.

## Boundary review notes

- Fixed graph: `STAGES` and `fixed_publication_adapters()` are exact over
  stages `10, 20, 21, 30, 31, 40, 50, 60, 70, 71`; public CLI run/resume use
  that registry.
- Stage gating: `publication_run()` writes run/effective config and executes
  only Stage 10; `publication_resume()` validates the completed-prefix manifests
  and advances only the next stage.
- Tools and drift: production registry binds repository-local Python and Poppler
  under `.tools` plus allowed system PowerShell/Word by SHA-256; `_load_run()`
  blocks stale implementation/config/local binding, and `_invoke_stage()`
  blocks runtime tool drift before stage writes.
- Stage 40: the adapter invokes only `translator/translator.py
  build-production-html`; command and receipt expose `direct_pdf_route: false`;
  local `src`/`href` references are inventoried and escape-checked.
- Stage 50: explicit DOCX config is required by the production adapter; transient
  Word bridge evidence is private, removed on success/failure, and any retained
  PDF or PDF-diagnostic JSON blocks the stage before manifesting.
- Stage 60: only `docx_acceptance` authority is accepted; supplied/pre-existing
  PDF authority is rejected; non-injected production path validates Word export
  evidence, fixed export arguments, cleanup, bound Word executable, exact
  input/output identity, and final all-page Poppler render evidence.
- Stage 70: package verification requires the ordered eight Stage 10-60
  manifests, six acceptance receipts, mandatory ArtView decisions/application/
  effective config, source/effective/derived configs, pipeline/schema snapshots,
  upstream source identity, and exactly one Stage 60 PDF.
- Stage 71: offline verification runs the package-copied stdlib verifier using
  `python -I`; success state is only `candidate_for_release_review` with
  `release_state=not_reviewed`.
- Legacy boundaries: accessible ArtView v2 tests remain green; no public
  direct HTML-to-PDF or legacy default route is authorized by Packet C.

## Recommendation

Proceed to the next bounded orchestration step for Packet C. Keep live
Dissociation publication, real user acceptance receipts, production promotion,
release review, Git commit/push, and any release claim pending. Close P2-1
before treating the schemas as release-grade standalone contracts.

## Changed files

- Added this receipt only:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_publication_packet_c_implementation_review_20260914.md`

## Closure review - Packet C P2-1 schema remediation

### Closure metadata

- Step id: `4PC-P2-1-closure`
- Review kind: `implementation`
- Reviewer role: independent critic, requested `gpt-5.5` / `medium`
- Platform identity: unavailable; role assignment state `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`; ownership not transferred
- Scoped override: none for critic role
- Timestamp: `2026-09-14T13:22:27+03:00`
- Elapsed time: unavailable in-receipt; final goal tool report should be treated
  as authoritative
- Token use: unavailable in-receipt; final goal tool report should be treated
  as authoritative
- Participation declaration: I did not implement or materially design the
  remediation. I reviewed the engineer receipt, current schemas, runtime, tests,
  and direct adversarial probes only.
- Changed files in this closure: appended this section only.

### Files checked for closure

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_publication_packet_c_implementation_review_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_packet_c_schema_remediation_20260914.md`
- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/contracts/publication_stage_manifest.v1.schema.json`
- `kb_creator/pipeline/publication.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_control_plane.py`
- `kb_creator/tests/test_publication_registry_e2e.py`

### Closure verdict

Reject P2-1 closure. The schema half and most runtime contract preflight
remediation are closed, but runtime tool-record parity remains incomplete for
the lower-level publication registry validator.

This is not a P0/P1 live-route blocker because public `publication run/resume`
construct production adapters through `fixed_publication_adapters()`, which
emits the intended four fixed tool records from concrete Python, Poppler,
PowerShell, and Word paths. However, the closure criterion explicitly required
closed injected versus exact four production tool record forms in both schema
and runtime. `_registry_tools()` still accepts arbitrary consistent production
tool records supplied through the reusable adapter API.

### Test evidence

Command:

```text
PYTHONPATH=C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI
C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe -m pytest -q kb_creator\tests\test_publication_contracts.py kb_creator\tests\test_publication_control_plane.py kb_creator\tests\test_publication_registry_e2e.py
```

Result:

```text
31 passed in 55.61s
```

### Passed closure checks

- `scenario_publication_contract.v1.schema.json` now has exact HTML and DOCX
  adapter constants: `translator_build_production_html_v1` and
  `production_docx_explicit_config_v1`.
- The five artifact-name regexes compile and reject slash/backslash path
  separators.
- `scenario_publication_contract.v1.schema.json` now requires exactly 22 unique
  package roles, and the enum set matches runtime `MANDATORY_PACKAGE_ROLES`.
- Runtime `publication_preflight()` rejects wrong HTML adapter, wrong DOCX
  adapter, missing package role, duplicate package role, extra package role, and
  backslash artifact names before creating the run root.

Representative runtime probe results:

```text
wrong_html_adapter -> PublicationControlError: invalid html adapter; run_root_absent=True
wrong_docx_adapter -> PublicationControlError: invalid docx adapter; run_root_absent=True
missing_role -> PublicationControlError: publication package roles must be the exact mandatory role set; run_root_absent=True
duplicate_role -> PublicationControlError: publication package roles must be the exact mandatory role set; run_root_absent=True
extra_role -> PublicationControlError: publication package roles must be the exact mandatory role set; run_root_absent=True
backslash_html_name -> PublicationControlError: artifact names must be stable basenames with expected suffixes; run_root_absent=True
```

- `publication_stage_manifest.v1.schema.json` now defines a closed `tools`
  `oneOf`: either the single injected-test record or exactly four production
  records with required names, scopes, and uppercase `sha256:<64 hex>` versions.

### Remaining finding

#### P2-1 remains open - runtime `_registry_tools()` accepts non-exact production tool declarations

Evidence:

Direct runtime probe of `kb_creator.pipeline.publication._registry_tools()` with
all ten stages declaring the same malformed production tool list produced these
acceptances:

```text
exact_four -> accepted=True count=4
extra_tool -> accepted=True count=5
bad_lowercase_sha -> accepted=True count=4
wrong_tool_name -> accepted=True count=4
missing_word -> accepted=True count=3
wrong_scope_but_allowed_enum -> accepted=True count=4
```

The current runtime checks each production-like record only for closed
`name/version/scope`, nonempty `name/version`, scope in
`repository_tools|allowed_system`, unique names within a stage, and equality
across stages. It does not enforce the exact four names, exact scope by name, or
uppercase `sha256:<64 hex>` pattern that the remediated schema now expresses.

Impact:

The public fixed-adapter CLI path remains safe, but the reusable runtime API and
stage-manifest verifier still do not fully match the exact schema contract for
production tool identities. This leaves the original schema/runtime parity
finding partially open and could allow internally constructed synthetic or
custom registries to create a sealed run/package with misleading production
tool identity metadata.

Required remediation:

- In `_registry_tools()`, accept exactly one of two forms:
  - injected form: exactly one record
    `{name: injected_publication_adapters, version: test, scope: injected_test}`;
  - production form: exactly four records with names
    `publication_python`, `pdftoppm`, `powershell`, `microsoft_word_com`,
    uppercase `sha256:<64 hex>` versions, and scopes
    `repository_tools`, `repository_tools`, `allowed_system`, `allowed_system`
    respectively.
- Reject mixed injected/production records, missing records, extra records,
  wrong names, wrong scopes, lowercase/bad SHA versions, duplicate names, and
  unknown fields before `run.json` can be written.
- Add direct runtime tests for those negative cases, not only schema-shape
  evaluator tests and not only `fixed_publication_adapters()` positive output.

### Remaining severity summary

- P0: none.
- P1: none.
- P2: P2-1 remains open, narrowed to runtime production tool-record exactness.

### Closure recommendation

Do not mark P2-1 closed yet. Patch the runtime tool-record exactness and add
direct negative tests, then run this same narrow closure again. Packet C's prior
P0/P1 approval remains unchanged, but schema/runtime parity is still pending
before schemas should be treated as release-grade standalone contracts.

## Final closure review - Packet C P2-1 runtime tool parity

### Final closure metadata

- Step id: `4PC-P2-1-final-closure`
- Review kind: `implementation`
- Reviewer role: independent critic, requested `gpt-5.5` / `medium`
- Platform identity: unavailable; role assignment state `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`; ownership not transferred
- Scoped override: none for critic role
- Timestamp: `2026-09-14T13:31:07+03:00`
- Elapsed time: unavailable in-receipt; final goal tool report should be treated
  as authoritative
- Token use: unavailable in-receipt; final goal tool report should be treated
  as authoritative
- Participation declaration: I did not implement or materially design this
  runtime parity remediation. I inspected current runtime/tests and repeated
  the prior malformed production-tool probes.
- Changed files in this closure: appended this final closure section only.

### Final closure verdict

Approve P2-1 closure. No remaining P0, P1, or P2 findings were identified in
the final closure scope.

The runtime now matches the remediated schema intent for publication tool
records: legacy all-`None` injected test adapters normalize to the single
explicit injected record; explicit injected records are accepted only in the
exact single-record form; production records are order-insensitive but normalize
to exactly `publication_python`, `pdftoppm`, `powershell`, and
`microsoft_word_com` with exact scopes and uppercase `sha256:<64 hex>`
versions.

This remains an implementation closure only. It does not authorize a live
Dissociation publication run, user acceptance recording, production promotion,
release review, Git mutation, or any direct HTML-to-PDF route.

### Final test evidence

Command:

```text
PYTHONPATH=C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI
C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe -m pytest -q kb_creator\tests\test_publication_contracts.py kb_creator\tests\test_publication_control_plane.py kb_creator\tests\test_publication_registry_e2e.py
```

Result:

```text
40 passed in 54.76s
```

### Final adversarial probe evidence

Direct runtime probes of `kb_creator.pipeline.publication._registry_tools()`:

```text
exact_injected_form -> accepted
legacy_all_None_injected_form -> normalized to injected_publication_adapters/test/injected_test
exact_production_ordered -> accepted
exact_production_shuffled_normalizes -> accepted and normalized to canonical order
extra_tool -> rejected: production publication tools must contain exactly four unique identities
missing_word -> rejected: production publication tools must contain exactly four unique identities
wrong_name -> rejected: production publication tool names are not exact
lowercase_sha -> rejected: production publication tool scope or SHA-256 identity is invalid
wrong_scope -> rejected: production publication tool scope or SHA-256 identity is invalid
duplicate -> rejected: production publication tools must contain exactly four unique identities
extra_field -> rejected: publication tool identity is not closed
mixed_same_stage -> rejected: production publication tools must contain exactly four unique identities
mixed_across_stages -> rejected: publication registry mixes production and injected tool identities
```

For each malformed production tool declaration also passed through
`publication_run()`, the run root remained absent, confirming zero-write
rejection before `run.json`, effective config, or Stage 10 output could be
created.

### Final remaining severity summary

- P0: none.
- P1: none.
- P2: none.

### Final recommendation

Packet C P2-1 is fully closed for implementation review. Packet C may proceed
under the already stated non-release boundaries: no live Dissociation
publication, no inferred acceptance, no production promotion, no release claim,
and no Git action without explicit user authorization.
