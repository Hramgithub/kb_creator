# Task packet: remediate Viral v2 identity review findings

## Role and ownership

- Owner: reuse `nri-engineer` (`gpt-5.6-terra`, medium) from the identity
  implementation.
- You are not alone in the worktree. Do not revert or change concurrent files.
- Read critic receipt SHA-256
  `C7657199B24463149693DFBF420FDFC6209ECBEED007E0C33AFFB3C05CD815BE`.

Owned paths only:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_reconstruction_identity_review_remediation_20260903.md`

## Required remediation

1. Builder maps missing configured root, missing CLI package, file,
   non-directory and resolved mismatch to
   `ValueError("v2 reconstruction package CLI/config path mismatch")` while
   keeping lexical unsafe-root errors separate.
2. Independent verifier maps the same filesystem/path-shape class to
   `E_V2_IDENTITY: reconstruction-package-cli`, keeping unsafe lexical root at
   `E_V2_IDENTITY: reconstruction-root`.
3. Add permanent builder/verifier tests for missing configured root, missing CLI
   package, CLI package is file and wrong directory. Add at least one CLI-level
   no-traceback assertion for missing path.
4. Add cheap P2 matrix coverage where portable: missing package object,
   lowercase/malformed digest, zero/negative count/bytes, add/delete/rename and
   same-length byte mutation. Add symlink/reparse/special tests only when they
   are deterministic on this Windows host; record any justified deferral.
5. Preserve exact v1 paths, aggregate semantics, helper no-write, candidate
   inventory and all frozen inputs.

## Verification and output

Run both focused modules, the current four-module baseline, both real v1
preflights and no-config/no-candidate/no-input-inventory checks. Write only the
assigned receipt and return `READY_FOR_V2_RECONSTRUCTION_IDENTITY_REREVIEW` with
exact hashes/tests, or a precise blocker. No full-partition work, config,
candidate or Git mutation.
