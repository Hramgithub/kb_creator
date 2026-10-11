# Independent critic receipt - neutral publication Packet B implementation review

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PB-publication-packet-b-implementation-review`
- Review kind: `implementation`
- Role: independent critic
- Requested model: `gpt-5.5`
- Requested reasoning effort: `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform
  identity unverified
- Assignment state: `platform-unverified`
- Scoped override: none
- Participation declaration: I did not implement or materially design Packet B.
  I reviewed the current worktree and wrote only this receipt.
- Timestamp: `2026-09-14T07:33:34+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:38:00`
- Token use: unavailable in-receipt; see task final/goal report if available

## Scope and files checked

Read or inspected:

- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_correction_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_publication_packet_a_implementation_review_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_packet_b_20260914.md`
- `kb_creator/contracts/scenario_artview_profile.v3.schema.json`
- `kb_creator/contracts/scenario_artview_decisions.v3.schema.json`
- `kb_creator/contracts/production_package_manifest.v1.schema.json`
- `kb_creator/pipeline/publication.py`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/scripts/scenario_master_ru.py`
- `kb_creator/scripts/scenario_artview.py`
- `kb_creator/scripts/scenario_artview_apply.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_scenario_master_ru.py`
- `kb_creator/tests/test_scenario_artview_v3.py`
- `kb_creator/tests/test_scenario_artview.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_control_plane.py`

Changed:

- Added this receipt only:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_publication_packet_b_implementation_review_20260914.md`

No product code, schemas, canonical plan/context/status/source/generated
outputs, `.codex`, release files, or Git state were edited by this review.

## Verdict

Reject Packet B as a basis for Packet C, live Dissociation publication, or any
new explicit acceptance gate until the P1 findings below are remediated and
independently re-reviewed.

No P0 was found: the public neutral publication runner remains disabled for
real production adapters, the DOCX-only PDF boundary was not reopened by Packet
B, and the focused synthetic suites pass. However, direct Packet B v3 CLIs and
functions currently have authority gaps that violate the architecture's exact
path/source-graph and acceptance-boundary requirements.

## Test evidence

Commands run with:

```text
PYTHONPATH=C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI
C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe
```

Results:

- `python -m pytest -q kb_creator\tests\test_publication_contracts.py kb_creator\tests\test_publication_control_plane.py kb_creator\tests\test_scenario_master_ru.py kb_creator\tests\test_scenario_artview_v3.py`
  - Result: `27 passed in 29.41s`
- `python -m pytest -q kb_creator\tests\test_build_scenario_master_en.py -k v3`
  - Result: `2 passed, 77 deselected in 0.47s`
- `python -m pytest -q kb_creator\tests\test_scenario_artview.py --deselect kb_creator/tests/test_scenario_artview.py::ScenarioArtViewTests::test_real_viral_bundle_contract_and_decision_validation`
  - Result: `9 passed, 1 deselected in 0.17s`
- Direct v2 ArtView run without deselection:
  - Result: `9 passed, 1 failed`
  - Classification: unavailable legacy generated fixture, not Packet B
    regression. The failure is
    `FileNotFoundError` for
    `kb_creator/inputs/viral/artview/review_checkpoint_20260909/candidate/candidate_manifest.json`.

Independent adversarial probes used OS temp directories and did not modify repo
state. They reproduced the P1 issues below.

## Findings

### P0

None.

### P1-1 - v3 direct content adapters can write successful candidates outside their authority root

Evidence:

- `kb_creator/scripts/build_scenario_master_en.py::build_v3_candidate()` accepts
  an absolute `target` and resolves it without requiring it to be under the
  profile/config authority root. The paired verifier
  `verify_scenario_master_en.py::verify_v3_candidate()` accepts the same
  absolute outside target.
- Direct probe result:

```text
{'build_status': 'candidate_built_for_independent_verification',
 'outside_exists': True,
 'under_fixture': False}
{'verify_status': 'verified_candidate_pending_process_and_external_gates'}
```

- `kb_creator/scripts/scenario_artview.py::build_v3()` accepts an absolute
  `output_root_arg` outside the profile root and returns
  `awaiting_artview_decisions`.
- Direct probe result:

```text
{'build_status': 'awaiting_artview_decisions',
 'outside_exists': True,
 'under_authority': False}
```

- `kb_creator/scripts/scenario_artview_apply.py::apply()` accepts an absolute
  `output_root` outside `authority_root` and returns `ready_for_html_candidate`.
- Direct probe result:

```text
{'apply_status': 'ready_for_html_candidate',
 'outside_exists': True,
 'under_authority': False}
```

Why this is P1:

- Packet B scripts are direct CLIs/functions even though the public production
  runner remains disabled. The architecture requires safe path/reparse/output
  containment, exact run-local candidates, no partial candidate, and no
  alternate authority paths. Successful writes outside the declared authority
  root break those guarantees and make later Packet C wiring unsafe.

Required remediation:

- For MASTER_EN v3, ArtView v3 bundle, and ArtView v3 apply, reject absolute
  output/candidate paths and any `..`, backslash, drive-qualified, existing
  symlink/reparse, or parent-reparse path.
- Require every direct output to resolve under the intended stage/run authority
  root, with an existing contained parent and absent final target.
- Make verifiers reject outside targets too; they must not legitimize a
  candidate the builder should never have written.
- Add negative tests for all three routes showing an absolute outside path
  fails before a candidate/output directory is created.

### P1-2 - ArtView v3 build accepts a non-closed upstream MASTER_RU acceptance receipt

Evidence:

- `kb_creator/scripts/scenario_artview.py::_v3_profile()` validates the
  MASTER_RU acceptance seal and selected fields, but does not enforce the closed
  `artifact_acceptance.v1` shape and does not resolve the receipt's producer
  stage or evidence identities.
- Direct probe: after adding an extra field to `master-ru.acceptance.json`,
  resealing it, and updating the profile input identity, `scenario_artview.build`
  still succeeded:

```text
{'built_with_nonclosed_master_ru_acceptance': 'awaiting_artview_decisions',
 'output_exists': True}
```

Why this is P1:

- Stage 30 requires exact accepted MASTER_RU authority. A sealed receipt with
  extra or invalid authority fields is not the closed acceptance document
  defined by Packet A. This weakens the explicit acceptance gate for every direct
  ArtView v3 bundle run.

Required remediation:

- In `_v3_profile()`, validate `master_ru_acceptance` with the same closed
  acceptance contract used by the publication control plane:
  exact field set, schema, scenario, artifact kind `master_ru`, decision
  `accepted`, recorder role `main_orchestrator`, candidate equality, producer
  identity, and every evidence identity resolved under the profile authority
  root.
- Add negative tests for extra receipt fields, invalid producer/evidence
  identity, wrong artifact kind, wrong recorder role, stale candidate, and
  unaccepted decision.

### P1-3 - ArtView v3 source-graph binding is SHA-only and permits same-byte alternate path spoofing

Evidence:

- `scenario_artview.py::_v3_profile()` builds `allowed_hashes` from
  `master_ru_asset_manifest.assets` and `reconstruction_inventory.artifacts`,
  then accepts row `current`, `context`, and `alternatives[*].binary` when their
  SHA-256 appears in that set.
- It does not require the row image path to match an exact path/bytes/SHA record
  in the bound source graph.
- Direct probe: a duplicate file with the same bytes as the declared current
  image but a different, unlisted path was accepted and copied into the bundle:

```text
{'built_with_same_hash_unlisted_current_path': 'awaiting_artview_decisions',
 'current_path_in_manifest': 'assets/current/map.png'}
```

Why this is P1:

- Packet B's ArtView v3 requirement is that all current/context/candidate
  binaries exist in the bound source graph and match path, bytes, SHA, media,
  and dimensions. SHA-only authorization allows alternate-path authority spoofing
  and loses source graph provenance even when bytes are identical.

Required remediation:

- Build an exact allowed binary identity set from the bound MASTER_RU asset
  manifest and reconstruction inventory, including path, bytes, SHA, and role
  or source graph membership.
- Require each profile row binary to match one exact graph record, not merely a
  SHA value.
- Add tests where an unlisted duplicate file with the same bytes is rejected for
  `current`, `context`, and candidate alternative images.

### P1-4 - Production package ArtView decisions validation is unreachable and evidence binding is weaker than exact-once

Evidence:

- In `kb_creator/pipeline/publication.py::verify_production_package()`, the call
  to `_validate_artview_decisions(role_map["artview_decisions"], ...)` is placed
  after an unconditional `raise` inside the Stage 60 DOCX-acceptance mismatch
  branch. When the normal branch is taken, that validation is skipped entirely.
- The later package check accepts ArtView decisions if any ArtView acceptance
  evidence row has matching `bytes` and `sha256`; it does not require the exact
  packaged decision identity to appear exactly once.
- A tampered-package probe changing packaged decisions to `draft`/open was
  rejected by stale Stage 31 acceptance authority before reaching this gap:

```text
{'baseline': 'candidate_for_release_review'}
{'tampered_rejected': 'PublicationControlError',
 'message': 'packaged Stage 31-artview-apply has stale artview_acceptance authority'}
```

  That positive chain check is useful, but it does not make the dead ArtView
  decision validation acceptable for an offline package verifier.

Why this is P1:

- The architecture requires the package verifier to prove accepted ArtView
  decisions are present, closed, reviewed, and bound. A dead validation call
  leaves the package verifier dependent on receipt/stage continuity and weakens
  the independent offline check Packet A/B promised.

Required remediation:

- Move `_validate_artview_decisions(role_map["artview_decisions"], manifest["scenario_id"])`
  into the normal verification path before the final return.
- Require
  `artview_acceptance["evidence"].count(file_identity(role_map["artview_decisions"])) == 1`
  using the full packaged path/bytes/SHA record, not only any bytes/SHA match.
- Add a regression where packaged `artview/decisions.json` is resealed as
  draft/open/incomplete and the package verifier rejects it after all dependent
  package identities are consistently resealed.

### P2

None.

## Positive checks retained

- Packet B and Packet A/control-plane focused suites pass in the repo-local
  `.tools` Python environment.
- MASTER_EN v3 rejects a `source_pdf` argument in preflight and independently
  rejects a tampered candidate body.
- MASTER_EN v3 inventory and acceptance binding reject same-byte alternate
  reconstructed-English paths through exact inventory/candidate path equality.
- MASTER_RU wrapper validates the exact accepted MASTER_EN receipt, ordered
  batch/unit identities, submission seal, closed review state, Markdown and
  mechanics parity signals, terminology presence, and absent output target
  before atomic assembly.
- ArtView v3 schemas are additive and do not contain Viral/Innsmouth constants.
- ArtView v2 non-live parity tests remain green when the missing generated
  Viral bundle fixture is explicitly deselected.
- `production_package_manifest.v1.schema.json` now reflects the prior Packet A
  P2 closure for exact stage-manifest and acceptance-receipt cardinalities and
  uniqueness.
- The neutral publication registry still does not expose a legacy direct
  HTML-to-PDF callable in the focused tests.

## Recommendation

Do not proceed to Packet C and do not run live Dissociation publication from
Packet B yet. Fix P1-1 through P1-4 with focused negative tests, rerun the 27
Packet B/control suite, the 2 MASTER_EN v3 tests, the accessible ArtView v2
parity tests, and the new adversarial path/acceptance/source-graph/package
tests, then request a narrow independent closure review.

This receipt is not reconstruction acceptance, publication acceptance, release
review, Git approval, or authorization to create live Dissociation artifacts.

## Next action

Engineering should patch direct v3 output containment and ArtView authority
validation first, then tighten the package verifier's reachable ArtView
decision validation. The next critic pass can be a bounded closure review if the
remediation receipt maps each P1 to code and tests.

## Closure review - Packet B P1 remediation

### Closure metadata

- Closure step id: `4PB-publication-packet-b-p1-remediation-closure`
- Review kind: `implementation`
- Role: independent critic
- Requested model: `gpt-5.5`
- Requested reasoning effort: `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform
  identity unverified
- Assignment state: `platform-unverified`
- Scoped override: none
- Participation declaration: I did not implement or materially design the
  remediation. I reviewed the current worktree and appended only this closure
  section.
- Timestamp: `2026-09-14T09:59:25+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `02:26:00`, dominated by an unusually slow focused
  pytest run on this host
- Token use: unavailable in-receipt; see task final/goal report if available

### Files checked

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_publication_packet_b_implementation_review_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_packet_b_remediation_20260914.md`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/scripts/scenario_artview.py`
- `kb_creator/scripts/scenario_artview_apply.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_scenario_artview_v3.py`
- `kb_creator/tests/test_publication_control_plane.py`
- `kb_creator/tests/test_scenario_artview.py`

Changed:

- Appended this closure section only.

No product code, schemas, canonical plan/context/status/source/generated
outputs, `.codex`, release files, or Git state were edited by this closure
review.

### Closure verdict

Approve Packet B P1 remediation. Prior findings P1-1 through P1-4 are closed in
the current worktree. Packet B may proceed to bounded Packet C implementation
planning/review, subject to the existing publication gates.

This approval does not authorize live Dissociation publication, user
acceptance recording, production-package promotion, release review, Git
operations, or any direct HTML-to-PDF route.

### Test evidence

Commands run with:

```text
PYTHONPATH=C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI
C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe
```

Results:

- `python -m pytest -q kb_creator\tests\test_publication_contracts.py kb_creator\tests\test_publication_control_plane.py kb_creator\tests\test_scenario_master_ru.py kb_creator\tests\test_scenario_artview_v3.py`
  - Result: `34 passed, 14 subtests passed in 6301.59s (1:45:01)`
- `python -m pytest -q kb_creator\tests\test_build_scenario_master_en.py -k v3`
  - Result: `3 passed, 77 deselected in 0.59s`
- `python -m pytest -q kb_creator\tests\test_scenario_artview.py --deselect kb_creator/tests/test_scenario_artview.py::ScenarioArtViewTests::test_real_viral_bundle_contract_and_decision_validation`
  - Result: `9 passed, 1 deselected in 0.17s`

The deselected v2 test still requires the absent generated Viral ArtView bundle
fixture previously documented by engineering and critic receipts. It is not a
Packet B remediation regression.

### Independent adversarial closure probes

All probes used OS temporary directories or in-memory monkeypatching for
reparse simulation and did not modify repository state.

P1-1 output containment:

- MASTER_EN v3 build rejected absolute outside target, drive-qualified path,
  backslash path, `../` path, and simulated reparse parent before output
  materialization.
- MASTER_EN v3 verifier rejected absolute outside target, drive-qualified path,
  backslash path, and `../` path even when a valid candidate existed elsewhere.
- ArtView v3 build rejected absolute outside target, drive-qualified path,
  backslash path, `../` path, and simulated reparse parent before output
  materialization.
- ArtView v3 apply rejected absolute outside target, drive-qualified path,
  backslash path, `../` path, and simulated reparse parent before output
  materialization.

Representative probe results:

```text
master_en_build_absolute -> ValueError: v3 candidate target must be safe authority-relative
master_en_verify_absolute -> ValueError: E_V3_PATH: candidate-target
artview_build_absolute -> ValueError: ArtView v3 output must be a safe authority-relative path
artview_apply_absolute -> ArtViewApplyError: ArtView application output must be a safe authority-relative path
artview_build_reparse_parent -> ValueError: ArtView v3 output contains an existing reparse path
artview_apply_reparse_parent -> ArtViewApplyError: ArtView application output contains an existing reparse path
```

P1-2 exact closed MASTER_RU acceptance:

- ArtView v3 build rejected resealed upstream MASTER_RU acceptance receipts
  with an extra field, stale candidate, wrong artifact kind, and unaccepted
  decision.
- Code inspection confirms `_v3_profile()` now requires the exact
  `artifact_acceptance.v1` field set, exact `master_ru` kind, `accepted`
  decision, `main_orchestrator` recorder, nonempty timestamp/reference, exact
  candidate equality, producer identity, nonempty unique evidence, and resolved
  producer/evidence files under profile authority.

Representative probe results:

```text
master_ru_acceptance_nonclosed -> ValueError: MASTER_RU acceptance closed schema mismatch
master_ru_acceptance_stale_candidate -> ValueError: MASTER_RU acceptance candidate mismatch
master_ru_acceptance_wrong_kind -> ValueError: ArtView v3 requires exact accepted MASTER_RU
master_ru_acceptance_unaccepted -> ValueError: ArtView v3 requires exact accepted MASTER_RU
```

P1-3 exact source-graph membership:

- Same-byte unlisted duplicate paths were independently rejected for ArtView v3
  `current`, `context`, and alternative candidate binaries.
- Code inspection confirms `_v3_graph_index()` now keys source-graph membership
  by resolved path, bytes, and SHA-256, and `_v3_bound_image()` requires an exact
  membership match rather than SHA-only authorization.

Probe results:

```text
same_byte_current -> ValueError: current image map is outside exact bound source graph
same_byte_context -> ValueError: context image map is outside exact bound source graph
same_byte_alternative -> ValueError: candidate image map-clean is outside exact bound source graph
```

P1-4 reachable package ArtView decision validation and exact-once evidence:

- Code inspection confirms `verify_production_package()` now calls
  `_validate_artview_decisions(role_map["artview_decisions"], manifest["scenario_id"])`
  on the normal package-verification path before stage-graph validation.
- Code inspection confirms packaged ArtView acceptance now requires
  `artview_acceptance["evidence"].count(decisions_identity) == 1`, using the
  full packaged path/bytes/SHA identity.
- A fully resealed package with draft/open/incomplete ArtView decisions was
  rejected with `ArtView decisions are not accepted and closed`.
- Fully resealed packages with duplicate exact decision evidence and
  same-byte/wrong-path decision evidence were rejected with
  `ArtView acceptance does not bind packaged decisions exactly once`.

Probe results:

```text
package_open_draft_artview_decisions -> PublicationControlError: ArtView decisions are not accepted and closed
package_duplicate_exact_artview_evidence -> PublicationControlError: ArtView acceptance does not bind packaged decisions exactly once
package_wrong_path_same_bytes_artview_evidence -> PublicationControlError: ArtView acceptance does not bind packaged decisions exactly once
```

### Regression/boundary checks

- No new P0, P1, or P2 findings were identified in the closure scope.
- v2 ArtView compatibility remains green for the accessible non-live tests.
- The public `publication run`/`resume` boundary remains covered by the focused
  control-plane suite; Packet C production adapters are still not authorized by
  this closure.
- The neutral publication registry/direct-route tests remain included in the
  focused suite; no legacy direct HTML-to-PDF route is authorized by this
  closure.
- The DOCX-only PDF boundary was not reopened by the Packet B remediation.

### Remaining findings

- P0: none.
- P1: none.
- P2: none.

### Closure recommendation

Packet B remediation is sufficient to close the prior implementation reject.
Proceed only to bounded Packet C work with a separate implementation receipt
and independent review. Keep all live Dissociation publication stages,
acceptance receipts, production-package promotion, and release review pending
until their own gates are satisfied.
