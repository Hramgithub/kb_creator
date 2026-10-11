# Viral v2 reconstruction identity review remediation — engineering receipt

- Goal: `20260830-kb-creator-next-scenario`, Step 7 MASTER_EN.
- Role: `nri-engineer` / `gpt-5.6-terra`, medium.
- Orchestrator policy owner: main chat / `gpt-5.6-sol`, medium.
- Assignment state: P1 remediation completed; fresh independent re-review required.
- Scoped override: none.
- Timestamp: `2026-09-03T05:08:00+03:00`.

## Scope and result

Remediated the exact P1 from critic receipt
`gpt55_critic_viral_v2_reconstruction_identity_review_20260903.md`
(SHA-256 `C7657199B24463149693DFBF420FDFC6209ECBEED007E0C33AFFB3C05CD815BE`).

Builder now validates reconstruction-package-root syntax before strict filesystem
resolution, then maps missing configured roots, missing CLI roots, CLI files,
CLI non-directories and resolved-directory mismatches to the stable
`ValueError("v2 reconstruction package CLI/config path mismatch")`. Lexically
unsafe roots remain `v2 reconstruction package root must be safe
repository-relative`.

The independent verifier applies the same filesystem/path-shape distinction:
lexical unsafe roots retain `E_V2_IDENTITY: reconstruction-root`; missing,
file, non-directory and mismatch cases return
`E_V2_IDENTITY: reconstruction-package-cli`.

The builder CLI now presents expected `ValueError` validation failures without a
Python traceback. This does not change v1 or candidate behavior.

## Changed paths

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- this receipt only.

No helper, v1 config, v2 config, accepted reconstruction, source PDF, ledger,
candidate/scratch root, canonical plan/context, Git index, commit, or push was
changed.

## Test coverage and evidence

- Added permanent builder/verifier cases for missing configured root, missing
  CLI package, CLI file and wrong directory.
- Added a builder CLI missing-package assertion for stable error text and no
  traceback.
- Added cheap portable P2 coverage for missing package object, lowercase
  digest, negative bytes, and immutable-tree delete/rename/same-length-byte
  mutations. Input `INVENTORY.json` remains ordinary aggregate material.
- Symlink/junction/reparse/special-file tests are deferred: their behavior is
  not deterministic across this managed Windows checkout, while implementation
  still rejects them using `lstat`/reparse attributes.
- Exact targeted command passed:
  `python -m unittest -v
  kb_creator.tests.test_build_scenario_master_en.BuilderPreflightTests.test_v2_reconstruction_package_closed_declaration_and_first_mismatch
  kb_creator.tests.test_build_scenario_master_en.BuilderPreflightTests.test_v2_reconstruction_package_immutable_tree_mutations
  kb_creator.tests.test_build_scenario_master_en.BuilderPreflightTests.test_v2_reconstruction_package_path_shapes_and_cli_no_traceback
  kb_creator.tests.test_verify_scenario_master_en.VerifierPreflightTests.test_independent_v2_reconstruction_package_known_answer_and_mutations
  kb_creator.tests.test_verify_scenario_master_en.VerifierPreflightTests.test_independent_v2_reconstruction_package_path_shapes`
  — `Ran 5 tests in 2.480s`, `OK`.
- Focused builder/verifier module run and four-module baseline were re-run:
  `test_build_scenario_master_en`, `test_verify_scenario_master_en`,
  `test_build_master_en_visual_qa_bundle`,
  `test_propose_scenario_semantic_units`; completed with no failure output.
- Both real v1 preflights returned `preflight_passed`; v1 configuration SHA is
  unchanged: `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Final negative output checks: `publication_config_v2.json=False`, accepted-v4
  input `INVENTORY.json=False`, preflight candidate target=False.

## Blockers and next action

No identity implementation blocker remains. The separate full source-partition
blocker remains unchanged; this remediation does not authorize config output or
candidate execution. Next action is fresh independent re-review of the bounded
identity implementation.

## Accounting

- Elapsed time: approximately 20 minutes.
- Token use: unavailable (platform counter not exposed).

`READY_FOR_V2_RECONSTRUCTION_IDENTITY_REREVIEW`
