# Critic receipt: pre-GPU publication increments

- Goal id: `20260914-dissociation-publication`
- Step id: `critic-pre-gpu-publication-increments`
- Review kind: `implementation`
- Role: independent critic
- Requested model / effort: `gpt-5.5` / `medium`
- Actual platform model / effort: unavailable
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol`, medium
- Assignment state: `platform-unverified`
- Scoped override: none for critic; engineering override remains out of scope
- Timestamp: `2026-09-14T14:07:53+03:00`
- Elapsed time: 206 seconds
- Token use: orchestrator-visible local goal counter `129303` at pre-write checkpoint

## Scope

Reviewed two bounded implementation increments only:

1. Publication blueprint schema, blueprint-to-contract author, tests, and
   engineer receipt.
2. Shared terminology changes in `scenario_master_ru.py`, Stage 70 terminology
   package retention in `publication_adapters.py`, tests, and engineer receipt.

This is not a release review, not live acceptance, and not an orchestration
ownership transfer. I did not edit implementation, canonical plan, canonical
context, project status, release files, or tests. I wrote only this handoff
receipt.

## Files Checked

- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_contract_authoring_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_shared_terminology_gate_20260914.md`
- `kb_creator/contracts/scenario_publication_blueprint.v1.schema.json`
- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/contracts/production_package_manifest.v1.schema.json`
- `kb_creator/scripts/author_scenario_publication_contract.py`
- `kb_creator/scripts/scenario_master_ru.py`
- `kb_creator/scripts/verify_production_package.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/tests/test_author_scenario_publication_contract.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_scenario_master_ru.py`
- `kb_creator/tests/test_publication_registry_e2e.py`
- `kb_creator/tests/test_production_package_verifier.py`

## Evidence

- Focused author/schema regression:
  `30 passed, 2 skipped in 1.20s`
  for `test_author_scenario_publication_contract.py` and
  `test_publication_contracts.py`.
- Focused MASTER_RU terminology regression:
  `9 passed, 6 subtests passed in 0.53s`
  for `test_scenario_master_ru.py`.
- Direct Stage 70 terminology copy guard:
  `1 passed in 0.85s`
  for
  `test_publication_registry_e2e.py::test_package_terminology_copy_rejects_duplicate_identity_and_drift_before_writes`.
- `py_compile` passed for the two reviewed scripts, adapter module, and scoped
  tests.
- Real selected terminology authorities parse together:
  `80` merged terms, `85` authority bindings, compatible overlaps:
  `Cthulhu Mythos`, `Drive Auto`, `Operate Heavy Machinery`, `Pilot`, `Ride`.
- Expanded publication registry/package run currently fails `7` tests with
  `invalid_or_unaccepted_reconstruction: fixed bridge authority is required`.
  The failure is tied to the newer reconstruction-promotion bridge authority
  preflight, not to the direct terminology copy guard.
- `git diff --check -- <reviewed files>` passed.

## Findings

### P1: Publication contract author accepts Windows ADS output targets

Evidence:

- `author_publication_contract()` only checks `os.path.lexists(output_path)`,
  the output parent reparse state, and parent directory existence before
  `output_path.open("xb")`
  (`kb_creator/scripts/author_scenario_publication_contract.py:376-431`).
- It does not reject `:` in `--output`, unlike config and terminology paths.
- Repro probe:
  an output path `contract.json:ads` returned `status: authored`,
  `exists: true`, `lexists: true`.
- Repro probe with an existing base file:
  `user-owned.json` existed and remained byte-unchanged, while
  `user-owned.json:contract` was created and the author reported `authored`.

Impact:

The author can create a hidden alternate data stream on Windows and can mutate
an existing user-owned filesystem object by adding a stream while bypassing the
visible-output/no-overwrite model. This violates the reviewed attack surface
for ADS paths, stable artifacts, and zero hidden writes. It also creates an
artifact that ordinary package/inventory tooling may not see as the authored
contract.

Recommendation:

Block integration of increment A until output paths are normalized and rejected
for drive, UNC, absolute escape, reparse, ADS/colon, and non-regular visible
file behavior before any validation staging or final write.

### P2: Blueprint and runtime validators accept whitespace-only semantic fields

Evidence:

- `_nonempty_string()` rejects only non-strings and empty strings, not strings
  whose `.strip()` is empty
  (`kb_creator/scripts/author_scenario_publication_contract.py:104-107`).
- `_unique_strings()` and `_validate_qa()` reject only empty string elements,
  not whitespace-only QA labels
  (`kb_creator/scripts/author_scenario_publication_contract.py:110-135`).
- Blueprint schema uses only `minLength: 1` for `title_en`, `title_ru`,
  profile fields, and required QA strings
  (`kb_creator/contracts/scenario_publication_blueprint.v1.schema.json:13-18`,
  `140-147`).
- Runtime `_validate_contract()` applies the same non-empty-only QA test
  (`kb_creator/pipeline/publication.py:306-309`), and the contract schema also
  uses `minLength: 1`.
- Repro probe authored a contract with:
  `title_en == '   '`, `master_en.profile == '   '`,
  `master_en.required_qa == ['   ']`.

Impact:

This does not directly permit filesystem escape or acceptance inference, but it
allows blank human-facing scenario labels, profile declarations, and QA policy
names to pass both schema and runtime validation. That can make a generated
contract look closed while carrying semantically empty policy labels.

Recommendation:

Require trimmed non-empty strings in the author and runtime validator, and add
schema patterns such as at least one non-whitespace code point for all
human/policy labels.

## Non-Finding Notes

- Duplicate JSON keys in blueprints are rejected during load.
- Config and terminology references reject traversal, drive, UNC, ADS/colon,
  backslash, absolute paths, missing files, empty files, and reparse/symlink
  references in the focused author tests.
- Generated contracts are checked by the private runtime validator before the
  exclusive final write.
- The shared terminology parser uses real `csv.DictReader`, strict table-row
  Markdown parsing, status filtering, normalized duplicate/conflict checks,
  per-unit source applicability, accepted target/alias matching, bad-variant
  blocking, and Unicode/casefold normalization.
- Stage 70 terminology copy validates exact identity, suffix, containment, and
  duplicate exact authority identity before writes. Tamper detection is covered
  by focused and prior package-verifier paths, but the current expanded E2E
  fixture is blocked by the out-of-scope bridge preflight noted above.
- I found no change to the exact package role count of `22`, no release-state
  claim, and no acceptance inference in the reviewed increments.

## Blockers

- Scoped integration blocker: P1 ADS output acceptance in increment A.
- Scoped non-blocking defect: P2 whitespace-only semantic fields in increment A.
- Current workspace integration blocker outside this scoped review: expanded
  registry/package tests that construct the older synthetic reconstruction
  authority now fail because the reconstruction-promotion bridge requires the
  fixed bridge authority. Route this to the bridge owner before live GPU use or
  expanded publication acceptance.

## Recommendation

Do not integrate these pre-GPU publication increments as-is. Increment B is
acceptable for integration within this scope if the out-of-scope bridge fixture
failure is handled separately, but increment A requires P1 remediation before
the combined pre-GPU set should advance.

Final acceptance, frozen-candidate approval, and release approval remain
pending and out of scope.
