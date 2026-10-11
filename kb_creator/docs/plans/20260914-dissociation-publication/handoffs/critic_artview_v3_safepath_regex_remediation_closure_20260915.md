# Critic closure receipt: ArtView v3 `safePath` regex remediation

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `artview-v3-safepath-schema-remediation`
- Review kind: `implementation`
- Role: independent critic
- Requested critic role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed candidate: no
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: none
- Timestamp: `2026-09-15T12:28:54+03:00`
- Elapsed time: approximately 20 minutes
- Token use: unavailable
- Scope: implementation closure only for ArtView v3 `safePath` schema/runtime/test remediation
- This is not a release review.

## Inputs and authority checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_artview_v3_safepath_regex_remediation_20260915.md`
  - SHA-256: `5D9A311F1244352A8B714F48E7A23F742CD7005180544432D7FBD071423D5B63`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_artview_v3_safepath_regex_remediation_20260915.md`
  - SHA-256: `83AF04AC7881BF95B3467FDC69E7DF682AD5D512C18D5208E345F594B3D66E2C`

## Files reviewed

- `kb_creator/contracts/scenario_artview_profile.v3.schema.json`
  - SHA-256: `F47B40474EB0A4A250997C7DC3A6B6C93ED649A991B367CA2FA8A2165F2B6875`
- `kb_creator/scripts/scenario_artview.py`
  - SHA-256: `8F52CE1E2BD87B5025F6124B4A09E71E470BCA588303A1D57EFC2E83B5F784F9`
- `kb_creator/tests/test_scenario_artview_v3.py`
  - SHA-256: `3DA414591E536E7276EDAE9883DBC7AC0D43103B74056440281887E4539C8C19`
- Read-only authored Dissociation profile:
  `kb_creator/inputs/dissociation/publication/v1/configs/artview/profile.json`
  - SHA-256 before/after probe: `D847123065C99DB39A41CD26949F0B74342E603AB2A604A5390CFEAB0376F18A`
  - bytes: `3018`

## Evidence

- The v3 schema loads as JSON and passes `Draft202012Validator.check_schema`.
- The decoded schema regex is exactly equal to `scenario_artview.V3_SAFE_PATH_PATTERN`:

```text
^(?!\s)(?!.*\s$)(?!/)(?!.*//)(?!.*(?:^|/)\.\.?(?:/|$))(?!.*[:\\\x00-\x1F])(?!.*(?:^|/)(?:[cC][oO][nN]|[pP][rR][nN]|[aA][uU][xX]|[nN][uU][lL]|[cC][oO][mM][1-9]|[lL][pP][tT][1-9])(?:\.|/|$))(?!.*[ .](?:/|$))[^/]+(?:/[^/]+)*$
```

- The runtime v3 helper compiles the same decoded regex via `V3_SAFE_PATH_RE` and `_v3_safe_path()` returns accepted values unchanged.
- `_v3_resolve()` and `_v3_output_root()` call `_v3_safe_path()` before `Path` construction, source lookup, output-root resolution, or output creation. The legacy `safe_relative()` remains separate and is not changed into the v3 validator.
- The remediation enforces portable forward-slash semantics: backslash, colon, absolute/UNC/drive paths, duplicate separators, dot/dotdot segments, trailing component dot/space, Windows reserved device names, leading/trailing whitespace, and ASCII controls are rejected.
- `test_scenario_artview_v3.py` covers:
  - exact schema/runtime regex parity;
  - schema validation at all three safePath use sites: `output_root`, input `path`, and image `path`;
  - safe Unicode/internal-space examples;
  - the authority unsafe matrix;
  - pre-filesystem/no-write rejection for `_v3_resolve()` and `_v3_output_root()`;
  - authored Dissociation profile validation with byte-preservation;
  - v3 build/decision closure behavior.
- The authored Dissociation ArtView profile validates under the corrected v3 schema, all 9 path-bearing values pass `_v3_safe_path()` unchanged, and profile bytes remained unchanged during the probe.
- ArtView v2 regression coverage was included in the broader test command. The only full-command failure is an unrelated absent legacy Viral fixture file; rerun excluding only that fixture is green.
- `git diff --check` over the three scoped remediation files passed.
- No contract authoring, publication preflight/stage, live materialize, acceptance recording, MinerU inference, CPU reconstruction, commit, or push was run.

## Commands and test results

```powershell
Get-FileHash kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_artview_v3_safepath_regex_remediation_20260915.md -Algorithm SHA256
Get-FileHash kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_artview_v3_safepath_regex_remediation_20260915.md -Algorithm SHA256
```

Result: hashes matched the assigned authority/engineer values.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q -rs kb_creator/tests/test_scenario_artview_v3.py
```

Result: `14 passed, 252 subtests passed in 2.68s`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q -rs kb_creator/tests/test_scenario_artview_v3.py kb_creator/tests/test_scenario_artview.py kb_creator/tests/test_publication_contracts.py kb_creator/tests/test_author_scenario_publication_contract.py
```

Result: `1 failed, 88 passed, 1 skipped, 252 subtests passed in 5.13s`.
The failure was only
`ScenarioArtViewTests.test_real_viral_bundle_contract_and_decision_validation`
because
`kb_creator/inputs/viral/artview/review_checkpoint_20260909/candidate/candidate_manifest.json`
is absent in this checkout. The skip was the existing Windows symlink privilege
limitation in `test_reparse_or_symlink_reference_is_rejected`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q -rs kb_creator/tests/test_scenario_artview_v3.py kb_creator/tests/test_scenario_artview.py kb_creator/tests/test_publication_contracts.py kb_creator/tests/test_author_scenario_publication_contract.py -k 'not test_real_viral_bundle_contract_and_decision_validation'
```

Result: `88 passed, 1 skipped, 1 deselected, 252 subtests passed in 5.19s`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -c '<read-only schema/profile parity probe>'
```

Result:

```text
schema_hash=F47B40474EB0A4A250997C7DC3A6B6C93ED649A991B367CA2FA8A2165F2B6875
profile_hash=D847123065C99DB39A41CD26949F0B74342E603AB2A604A5390CFEAB0376F18A
profile_bytes=3018
profile_path_count=9
profile_schema_validation=PASS
profile_byte_unchanged=PASS
```

```powershell
& '.tools/PortableGit/cmd/git.exe' diff --check -- kb_creator/contracts/scenario_artview_profile.v3.schema.json kb_creator/scripts/scenario_artview.py kb_creator/tests/test_scenario_artview_v3.py
```

Result: PASS, no whitespace errors reported.

## Findings

- P0: none.
- P1: none.
- P2: unrelated legacy Viral fixture gap remains in this checkout:
  `kb_creator/inputs/viral/artview/review_checkpoint_20260909/candidate/candidate_manifest.json`
  is absent, so the broad unfiltered v2 fixture test cannot pass here. This does
  not block the scoped ArtView v3 safePath remediation or config-author resume.
- P2: Windows symlink privilege limitation persists for the reparse/symlink
  adversarial test, which is skipped by the existing test guard. This is an
  environment limitation, not evidence of a remediation defect.

## Recommendation

**GO** to resume config author contract validation and read-only publication
preflight after this implementation closure.

Do not treat this as authorization for live Stage 10, publication materialize,
acceptance recording, release approval, commit, or push.

## Blockers

None for the scoped ArtView v3 safePath remediation closure.

