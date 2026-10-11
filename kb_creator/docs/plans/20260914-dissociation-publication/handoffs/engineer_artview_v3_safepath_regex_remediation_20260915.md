# Engineer receipt: ArtView v3 `safePath` regex remediation

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `artview-v3-safepath-schema-remediation`
- Role: engineer under the recorded `gpt-5.6-sol` / `high` override
- Timestamp: `2026-09-15T12:24:45+03:00`
- Authority: `architect_artview_v3_safepath_regex_remediation_20260915.md`
- Authority SHA-256: `5D9A311F1244352A8B714F48E7A23F742CD7005180544432D7FBD071423D5B63`
- Result: PASS; bounded implementation and focused verification complete
- Live actions: none; no contract authoring, publication preflight/stage, acceptance, MinerU inference, CPU reconstruction, commit, or push

## Implemented change

- Replaced the invalid/weak ArtView v3 `$defs.safePath.pattern` with the exact
  portable forward-slash regex specified by the authority receipt.
- Added `V3_SAFE_PATH_PATTERN`, its compiled regex, and `_v3_safe_path()` to the
  ArtView implementation.
- `_v3_resolve()` and `_v3_output_root()` now reject invalid lexical paths before
  constructing `Path` objects or consulting the filesystem. Accepted strings are
  returned unchanged; no slash conversion is performed.
- Kept the shared legacy `safe_relative()` and all ArtView v2 dispatch/behavior
  unchanged.
- Added schema compile/check, schema/runtime parity, all-three-use-site rejection,
  pre-filesystem/no-write, safe Unicode/internal-space, and real authored-profile
  byte-preservation coverage.

## Identity evidence

- `kb_creator/contracts/scenario_artview_profile.v3.schema.json`
  - corrected SHA-256: `F47B40474EB0A4A250997C7DC3A6B6C93ED649A991B367CA2FA8A2165F2B6875`
  - bytes: `3962`
- `kb_creator/scripts/scenario_artview.py`
  - observed working-tree SHA-256: `8F52CE1E2BD87B5025F6124B4A09E71E470BCA588303A1D57EFC2E83B5F784F9`
  - bytes: `135605`
- `kb_creator/tests/test_scenario_artview_v3.py`
  - SHA-256: `3DA414591E536E7276EDAE9883DBC7AC0D43103B74056440281887E4539C8C19`
  - bytes: `22944`
- Read-only authored Dissociation profile
  `kb_creator/inputs/dissociation/publication/v1/configs/artview/profile.json`
  - SHA-256 before/after: `D847123065C99DB39A41CD26949F0B74342E603AB2A604A5390CFEAB0376F18A`
  - bytes before/after: `3018`
  - Draft 2020-12 instance validation: PASS

The schema file and v3 test file were already untracked working-tree artifacts
when this packet began; the implementation file also contained pre-existing
uncommitted v3 work. This packet changed only the owned safe-path portions and
did not revert or rewrite adjacent work.

## Verification

Interpreter: repository-local `.tools/MinerU/.venv/Scripts/python.exe` used only
as Python; no MinerU command/model and no reconstruction CPU stage was invoked.
Dependencies: `PYTHONPATH=.tools/python-test-deps`; nothing installed.

1. `python -m py_compile kb_creator/scripts/scenario_artview.py kb_creator/tests/test_scenario_artview_v3.py`
   - PASS.
2. `python -m pytest -q -rs kb_creator/tests/test_scenario_artview_v3.py`
   - PASS: `14 passed, 204 subtests passed`.
3. Focused ArtView v3/v2 + publication contracts/registry + contract-author run:
   - first run: `93 passed, 1 skipped, 1 failed, 252 subtests passed`;
   - the sole failure is a pre-existing absent legacy Viral fixture:
     `kb_creator/inputs/viral/artview/review_checkpoint_20260909/candidate/candidate_manifest.json`;
   - rerun excluding only
     `test_real_viral_bundle_contract_and_decision_validation`: PASS,
     `93 passed, 1 skipped, 1 deselected, 252 subtests passed`;
   - skip is the existing Windows privilege limitation for symlink creation in
     `test_reparse_or_symlink_reference_is_rejected` (`WinError 1314`).
4. `git diff --check` over the three owned implementation/test/schema paths:
   PASS.

The test matrix accepts `profile.json`, `assets/map-01.jpg`,
`кисти/карта 01.webp`, and `a.b/c-d_1.png`. It rejects the authority's complete
absolute/UNC/drive, dot-segment, separator, ADS/URI, whitespace, trailing
dot/space, reserved-device, and ASCII-control matrix at `output_root`, input
file, image file, `_v3_resolve`, and `_v3_output_root` use sites without writes.

## Findings and blockers

- P0: none.
- P1: closed. The schema compiles, passes `Draft202012Validator.check_schema`,
  and is lexically identical to the runtime v3 validator.
- P2: environmental regression-fixture gap remains: the legacy Viral candidate
  manifest is absent, so that unrelated read-only fixture test cannot pass in
  this checkout. No owned-file remediation is appropriate.
- Blockers to bounded implementation: none.
- Independent implementation review remains required before contract authoring
  or publication preflight resumes, per the authority receipt.

## Next action

Independent critic reviews the three-file safe-path remediation and this
evidence. On closure, the orchestrator may unblock config schema validation,
generic contract authoring, and read-only publication preflight. No live Stage
10 or acceptance is authorized by this receipt.
