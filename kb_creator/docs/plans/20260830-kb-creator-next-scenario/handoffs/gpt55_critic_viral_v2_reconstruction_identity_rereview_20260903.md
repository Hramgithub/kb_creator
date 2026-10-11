# Viral v2 reconstruction identity - independent rereview receipt

- Goal: `20260830-kb-creator-next-scenario`, Step 7 MASTER_EN.
- Review kind: implementation.
- Reviewer role: `nri-independent-critic` / requested `gpt-5.5`, high, platform-unverified.
- Implemented or materially designed candidate: no.
- Orchestrator policy owner: main chat / `gpt-5.6-sol`, medium.
- Assignment state: assigned independent rereview completed.
- Scoped override: none.
- Timestamp: `2026-09-03T05:01:28.2774038+03:00`.

## Review target

Bounded rereview packet:
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/TASK_PACKET_gpt55_critic_viral_v2_reconstruction_identity_rereview_20260903.md`.

Bound source receipts:

- Architecture receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_v2_reconstruction_identity_20260903.md`
  SHA-256 `83C917A4A75DBFA8F1EC88ACC5C7248B6D6F772534DD4905DAB9971035664F5D`.
- Prior changes-required critic receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_reconstruction_identity_review_20260903.md`
  SHA-256 `C7657199B24463149693DFBF420FDFC6209ECBEED007E0C33AFFB3C05CD815BE`.
- P1 remediation receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_reconstruction_identity_review_remediation_20260903.md`
  SHA-256 `32FECDA76A8ADB26A7785DF1182D6E95C062CE3F3891A3C526A8BE28DB2E31F0`.

Checked implementation/test files at rereview time:

- `kb_creator/scripts/build_scenario_master_en.py`
  SHA-256 `FBD342F1742DE11F7DDB7093946216D24ED5F2FC21AEEBF87955D8DA171B86B1`.
- `kb_creator/scripts/verify_scenario_master_en.py`
  SHA-256 `DEFBF82C833E91131A31AF29094BBEE90CB5DB017DC281613DDA00028115FC7A`.
- `kb_creator/scripts/author_viral_master_en_v2_config.py`
  SHA-256 `3FD74EF9933C2D327A64250F719EAD454A6C998279A61C5F9075E66EA71F1FD7`.
- `kb_creator/tests/test_build_scenario_master_en.py`
  SHA-256 `87A607AF394E05189232FE01C92EFD9AE3AEE1798932D0C284585A7ACACF79BE`.
- `kb_creator/tests/test_verify_scenario_master_en.py`
  SHA-256 `A534E843142D8BE3C936596CC2B3BB212AAA2C50974AA3D197BADF30300475CB`.

## Evidence

- Source inspection confirmed builder keeps unsafe lexical roots separate from
  filesystem path-shape failures: `v2_safe_package_root()` validates safe
  repository-relative syntax before strict resolution, and `v2_input_binding()`
  maps missing configured root, missing CLI root, CLI file, non-directory and
  wrong directory to `ValueError("v2 reconstruction package CLI/config path mismatch")`.
- Source inspection confirmed the independent verifier maps lexical unsafe
  root to `E_V2_IDENTITY: reconstruction-root` and missing/file/non-directory
  or mismatched configured/CLI package to
  `E_V2_IDENTITY: reconstruction-package-cli`.
- Source inspection confirmed verifier v2 package inventory is independently
  implemented and includes every regular filename, including an input
  `INVENTORY.json`; builder candidate inventory remains the separate
  self-excluding output contract.
- Required five targeted cases passed:
  `python -m unittest -v
  kb_creator.tests.test_build_scenario_master_en.BuilderPreflightTests.test_v2_reconstruction_package_closed_declaration_and_first_mismatch
  kb_creator.tests.test_build_scenario_master_en.BuilderPreflightTests.test_v2_reconstruction_package_immutable_tree_mutations
  kb_creator.tests.test_build_scenario_master_en.BuilderPreflightTests.test_v2_reconstruction_package_path_shapes_and_cli_no_traceback
  kb_creator.tests.test_verify_scenario_master_en.VerifierPreflightTests.test_independent_v2_reconstruction_package_known_answer_and_mutations
  kb_creator.tests.test_verify_scenario_master_en.VerifierPreflightTests.test_independent_v2_reconstruction_package_path_shapes`
  returned `Ran 5 tests in 2.794s`, `OK`.
- Focused four-module baseline passed:
  `python -m unittest -q
  kb_creator.tests.test_build_scenario_master_en
  kb_creator.tests.test_verify_scenario_master_en
  kb_creator.tests.test_build_master_en_visual_qa_bundle
  kb_creator.tests.test_propose_scenario_semantic_units`
  returned `Ran 73 tests in 35.567s`, `OK`.
- `python -m py_compile kb_creator/scripts/build_scenario_master_en.py
  kb_creator/scripts/verify_scenario_master_en.py
  kb_creator/scripts/author_viral_master_en_v2_config.py` exited `0`.
- Real frozen v1 builder preflight returned `preflight_passed`, source SHA-256
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`, contract
  SHA-256 `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`,
  and reconstruction aggregate
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Real frozen v1 verifier preflight returned `preflight_passed` and
  `publication_config_sha256 =
  C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Final forbidden-output checks returned `False` for
  `kb_creator/working/viral/master_en/publication_config_v2.json`,
  accepted-v4 input `INVENTORY.json`,
  `kb_creator/working/synthetic`,
  `kb_creator/working/viral/master_en/phase_a_test_target`, and
  `kb_creator/working/viral/master_en/candidates/path-shape`.

## Findings

P0: none.

P1: none. The prior first-error contract blocker is closed in both builder and
independent verifier, and the builder CLI no-traceback regression is covered by
the targeted path-shape test.

P2: nonblocking hardening remains for symlink, junction/reparse and special-file
topology as permanent portable tests. The remediation receipt explicitly defers
these rows because they are not deterministic across this managed Windows
checkout; the implementation still has topology rejection paths using
`lstat`/reparse checks, and no P1 depends on accepting those files.

## Blockers

No blocker remains in the bounded v2 reconstruction identity rereview scope.

The separate publication completeness/source-partition blocker remains outside
this approval. The architecture states that the boundary ledgers identify
special structures rather than a complete source partition; this rereview does
not claim completeness is solved and does not authorize config output or
candidate execution by itself.

## Recommendation

Accept the bounded identity remediation. The orchestrator may close the v2
reconstruction-package identity gate for the reviewed file hashes above.
Continue to block config authoring and candidate execution until the separately
scoped completeness/partition gate is designed, implemented, and reviewed.

Terminal decision:

`APPROVED_V2_RECONSTRUCTION_IDENTITY`

## Accounting

- Elapsed time: approximately 25 minutes.
- Token use: 129,529 tokens from the local goal counter after completion;
  role-specific platform contributor split unavailable.
