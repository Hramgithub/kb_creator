# Viral v2 reconstruction identity - independent implementation review

- Goal: `20260830-kb-creator-next-scenario`, Step 7 MASTER_EN.
- Review kind: implementation.
- Reviewer role: `nri-independent-critic` / `gpt-5.5`, high, platform-unverified.
- Implemented or materially designed candidate: no.
- Orchestrator policy owner: main chat / `gpt-5.6-sol`, medium.
- Assignment state: assigned independent review completed.
- Scoped override: none.
- Timestamp: `2026-09-03T04:29:16.5963108+03:00`.

## Review target

Architecture receipt:
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_v2_reconstruction_identity_20260903.md`
with SHA-256
`83C917A4A75DBFA8F1EC88ACC5C7248B6D6F772534DD4905DAB9971035664F5D`.

Engineering receipt:
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_reconstruction_identity_20260903.md`
with SHA-256
`5426D05F9C9A5EBA4197F6E698D77E171C6369191EF63B08F06FFAF2E40EE35F`.

Checked implementation/test files:

- `kb_creator/scripts/build_scenario_master_en.py`
  SHA-256 `D9E60B48A0FF5882FA743EEB1C9560B3CE16B13EAE28873F72006F1BE623E952`.
- `kb_creator/scripts/verify_scenario_master_en.py`
  SHA-256 `203084EF6D4A96F696DDB4ECF5C29DF170DEFF35D5A96EED85DE70BF1C5F2A6A`.
- `kb_creator/scripts/author_viral_master_en_v2_config.py`
  SHA-256 `3FD74EF9933C2D327A64250F719EAD454A6C998279A61C5F9075E66EA71F1FD7`.
- `kb_creator/tests/test_build_scenario_master_en.py`
  SHA-256 `76D513D4F8CA5AD7C5AEA07296343BF79FA6224C22EC09202DA743685DD3BFCA`.
- `kb_creator/tests/test_verify_scenario_master_en.py`
  SHA-256 `2B8ACB4E76544C535691BF99A5D677080BB3119CCE2FE5357D51E8B37A612C6D`.
- Frozen v1 working config
  `kb_creator/working/viral/master_en/publication_config_v1.json`
  SHA-256 `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

## Evidence

- Source inspection confirmed builder defines the v2 aggregate package hash path
  separately from candidate inventory in `build_scenario_master_en.py`
  around `v2_safe_package_root`, `v2_package_inventory`,
  `v2_config`, and `v2_input_binding`.
- Source inspection confirmed verifier independently defines its own
  `v2_package_path`, `v2_package_inventory`, `v2_contract`,
  `v2_input_binding`, `v2_report_payload`, and `verify_v2_candidate`, and the
  verifier script source does not import `build_scenario_master_en`.
- `python -m unittest -v kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en`
  passed: 70 tests in 34.452s.
- `python -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en kb_creator.tests.test_build_master_en_visual_qa_bundle kb_creator.tests.test_propose_scenario_semantic_units`
  passed: 70 tests in 33.173s.
- `python -m py_compile kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py kb_creator/scripts/author_viral_master_en_v2_config.py`
  passed.
- Real v1 builder preflight passed with
  `reconstruction_inventory_sha256 =
  68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Real v1 verifier preflight passed with
  `publication_config_sha256 =
  C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Helper import/no-write probe returned `before = false`, `after = false`,
  `root_inventory_exists = false`, and identity
  `(377, 41079424,
  68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83)`.
- Targeted unsafe-root probe confirmed both builder and verifier reject
  `/abs`, `C:/abs`, `a\b`, empty string, `.`, `a//b`, and `../x`.
- Final side-effect checks returned false for
  `kb_creator/working/synthetic`,
  `kb_creator/working/viral/master_en/publication_config_v2.json`, and
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/INVENTORY.json`.

## Findings

### P1 - v2 builder and verifier do not fully meet the required first-error contract for missing reconstruction package paths

The architecture required missing/not-directory/CLI mismatch cases to fail as
stable v2 identity errors after schema/root syntax validation. The current
implementation does not meet that for missing package paths:

- Builder `v2_input_binding` resolves the CLI package with
  `Path(reconstruction_package).resolve(strict=True)` before mapping failures to
  a `ValueError`. A missing CLI package therefore raises uncaught
  `FileNotFoundError` instead of the required stable builder
  `ValueError` surface.
- Builder `v2_safe_package_root` also resolves the configured package root with
  `strict=True` without catching filesystem failure. A missing configured root
  raises uncaught `FileNotFoundError`.
- Verifier handles a missing CLI package correctly as
  `E_V2_IDENTITY: reconstruction-package-cli`, but a missing configured
  package root is currently classified as
  `E_V2_IDENTITY: reconstruction-root`. That is the unsafe-root bucket, not the
  missing/not-directory/CLI mismatch bucket specified by the architecture.

Targeted probe evidence:

```text
builder missing CLI package -> FileNotFoundError
builder file CLI package -> ValueError: v2 reconstruction package CLI/config path mismatch
builder wrong_dir CLI package -> ValueError: v2 reconstruction package CLI/config path mismatch
verifier missing CLI package -> ValueError: E_V2_IDENTITY: reconstruction-package-cli
verifier file CLI package -> ValueError: E_V2_IDENTITY: reconstruction-package-cli
verifier wrong_dir CLI package -> ValueError: E_V2_IDENTITY: reconstruction-package-cli
builder missing configured root -> FileNotFoundError
verifier missing configured root -> ValueError: E_V2_IDENTITY: reconstruction-root
```

This is not a content corruption bug and does not mutate v4, but it is a
blocker for `APPROVED_V2_RECONSTRUCTION_IDENTITY` because the assignment
explicitly asked to catch first-error mismatches and missing package path
classes.

Required remediation:

- In builder, catch `OSError`/`RuntimeError`/`ValueError` around strict
  resolution of both the configured `document.reconstruction_package.root` and
  the CLI `--reconstruction-package`, and map missing/file/not-directory/path
  mismatch to `ValueError("v2 reconstruction package CLI/config path mismatch")`.
- Keep lexical unsafe-root rejection separate as
  `ValueError("v2 reconstruction package root must be safe repository-relative")`.
- In verifier, keep lexical unsafe-root failures as
  `E_V2_IDENTITY: reconstruction-root`, but map missing configured roots,
  missing CLI roots, files, non-directories, and resolved mismatch to
  `E_V2_IDENTITY: reconstruction-package-cli`.
- Add explicit builder and verifier tests for missing configured root, missing
  CLI package, CLI package is file, and wrong directory. At least one CLI-level
  regression should assert no traceback is emitted for the missing-path case.

### P2 - negative coverage is not yet explicit for the full architecture matrix

The focused tests cover the main aggregate known answer, stale count/bytes/digest
order, legacy `reconstruction_inventory`, an extra package key, boolean
`file_count`, wrong algorithm, one unsafe root, empty directory topology, input
`INVENTORY.json` counted as ordinary material, source/page identity negatives,
and candidate inventory mutation behavior.

Several matrix rows are still only partially covered by source inspection or
manual probes rather than permanent automated tests: missing
`reconstruction_package`, malformed/lowercase digest, negative count/bytes,
configured-root missing/file/wrong-dir, delete/rename/same-length package
mutation, and symlink/reparse/special file topology. The P1 remediation should
at minimum add the path-shape cases above; the remaining rows can be added as
follow-up hardening if they are expensive on Windows.

## Blockers

- P1 first-error contract mismatch for missing reconstruction package paths.

## Recommendation

Do not reopen v2 config authoring from this checkpoint yet. The aggregate
identity design is otherwise on the right path, and the accepted v4 known answer,
v1 preflights, helper no-write property, and candidate inventory separation all
held under review. Fix the missing-path error mapping and add the explicit
negative tests, then rerun focused builder/verifier tests and request a short
independent re-review.

Terminal decision:

`CHANGES_REQUIRED_V2_RECONSTRUCTION_IDENTITY`

## Accounting

- Elapsed time: approximately 30 minutes.
- Token use: unavailable; no active goal usage counter exposed in this review
  task.
