# Engineering receipt - publication Packet B P1 remediation

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PB-publication-packet-b-p1-remediation`
- Role: engineering
- User-scoped role override: `gpt-5.6-sol` at `high`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Scope: synthetic Packet B/control-plane remediation only

No live Dissociation source or output was read, generated, accepted, or
released. Canonical plan/context/status, `.codex`, Packet C adapters, legacy
translation primitives, and Git state were not changed by this step.

## Root causes and closure

### P1-1 - direct output authority

Root cause: the new v3 functions resolved caller-provided output paths before
proving that they were authority-relative. Absolute paths could therefore be
materialized and later legitimized by the paired verifier.

Closure:

- MASTER_EN v3 builder and independent verifier now require a forward-slash,
  authority-relative target with no drive qualifier, backslash, empty/dot/dotdot
  component, outside resolution, or existing symlink/reparse component.
- ArtView v3 build and ArtView v3 apply use the same fail-closed semantics.
- A target's parent must already exist and remain contained; a build/apply
  target must be absent, while a verifier target must be an existing contained
  non-reparse directory.
- All checks run before staging or output writes.
- Negative tests prove no outside directory is created by MASTER_EN build,
  ArtView build, or ArtView apply, and that MASTER_EN verification rejects an
  absolute target even when it names a valid candidate.

### P1-2 - closed MASTER_RU acceptance

Root cause: ArtView v3 checked the acceptance seal and a selected subset of
fields, but did not enforce the closed `artifact_acceptance.v1` field set or
resolve producer/evidence authorities.

Closure:

- `_v3_profile` now requires the exact acceptance field set, schema and
  scenario, `master_ru` kind, `accepted` decision, `main_orchestrator` recorder,
  nonempty decision timestamp and user reference, and exact candidate equality
  with the bound MASTER_RU identity.
- The producer stage and every nonempty, unique evidence identity are resolved
  with exact path/bytes/SHA under the profile authority root, including existing
  reparse-component rejection.
- A negative matrix covers extra fields, wrong schema/scenario/kind/role,
  missing producer/evidence, empty evidence, stale candidate, unaccepted
  decision, and empty user reference.

### P1-3 - exact source graph membership

Root cause: current, context, and alternative binaries were authorized by an
allowed SHA set, allowing an unlisted path containing identical bytes.

Closure:

- Both bound source graphs are indexed by the resolved exact path plus bytes
  plus SHA, with each graph record independently resolved relative to its
  manifest authority.
- Every current/context/alternative image must match one exact graph record;
  media type and dimensions remain validated from decoded image bytes.
- The portable candidate manifest preserves each match as source graph name,
  source role (or a deterministic source-class fallback), and original exact
  identity.
- Adversarial subtests reject same-byte unlisted paths for current, context,
  and alternative binaries.

### P1-4 - reachable package decision validation

Root cause: `_validate_artview_decisions` was indented after an unconditional
raise and therefore unreachable on valid packages; evidence matching ignored
the packaged path and cardinality.

Closure:

- The production package verifier now validates the packaged ArtView decision
  document on the normal path before upstream stage-chain acceptance.
- The packaged ArtView acceptance must contain the exact packaged
  path/bytes/SHA identity exactly once.
- Synthetic package fixtures preserve the run-local decision path inside the
  package. Tests reseal changed decision/acceptance documents, dependent stage
  manifests and acceptance producer identities, package inventories, and the
  production manifest.
- A fully resealed draft/open/incomplete decision document is rejected.
  Duplicate exact evidence and a same-byte evidence record at a different path
  are independently rejected.

## Files changed in this remediation

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/scripts/scenario_artview.py`
- `kb_creator/scripts/scenario_artview_apply.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_scenario_artview_v3.py`
- `kb_creator/tests/test_publication_control_plane.py`
- this receipt

## Verification

Environment:

- interpreter: `.tools/MinerU/.venv/Scripts/python.exe`
- `PYTHONPATH=.tools/python-test-deps;<repository-root>`

Results:

- `py_compile` for all five changed implementation modules and all three
  changed test modules: pass.
- `pytest -q test_publication_contracts.py test_publication_control_plane.py test_scenario_master_ru.py test_scenario_artview_v3.py`:
  `34 passed, 14 subtests passed`.
- `pytest -q test_build_scenario_master_en.py -k v3`:
  `3 passed, 77 deselected`.
- `pytest -q test_scenario_artview.py --deselect ...::test_real_viral_bundle_contract_and_decision_validation`:
  `9 passed, 1 deselected`.
- repository `git diff --check`: pass; only pre-existing CRLF conversion
  warnings were printed for unrelated/shared working-tree files.

The intentionally deselected v2 test still depends on the absent generated
Viral ArtView fixture documented in the original Packet B and critic receipts;
it is not a Packet B remediation regression. Per assignment, no long unrelated
suite or live scenario run was performed.

## Remaining risks and next action

- Windows reparse detection is implemented for both final targets and existing
  parent components. The focused suite exercises containment/no-write behavior;
  it does not create a privileged Windows junction fixture.
- Candidate-manifest source membership is a Packet B runtime contract rather
  than a separately published schema. Packet C must consume it without
  weakening the exact source-graph check.
- This receipt is engineering evidence, not independent approval, artifact
  acceptance, live-run authorization, or release review.

Next action: request a narrow independent Packet B closure review of P1-1
through P1-4 before Packet C or any live Dissociation publication action.
