# Task packet — Viral v2 A2 full structured-evidence mutation matrix closure

- Role: fresh/recovered `nri-engineer` / GPT-5.6-terra / medium, test-only.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Preserve unrelated edits; do not revert others.
- Current fixed hashes:
  - builder `76DDF943D84B23A60578189F2E1C808D4606AD67028FFCCE76E0DD50418C4E3F`;
  - verifier `938A6D3635E2078D20D09A32F9792808915E23CE909D1C7BDDD81ACB08B36CFE`;
  - builder tests `6C94EE0A0D0ED069F7E38CC52D911E7AC216E05D89672E51FC6CA013EC7E2098`;
  - verifier tests `3C03F3305EF6EBC8B8601CA1F742E55F97BEF3B49E136BEBA09FCF90206F2B18`.
- The verifier-test hash includes the orchestrator's one-line stale fixture
  correction from fake ref `viral` to exact ref
  `viral-logical_table-p020-l025`; preserve it.

Own only the two focused test files and new receipt
`terra_engineering_viral_v2_complete_authoring_phase_a2_full_mutation_matrix_closure_20260903.md`.
Production scripts are read-only. If any mutation exposes a production defect,
stop and return CHANGES_REQUIRED with reproduction. Do not edit prior receipts,
helper/config/evidence/inputs/A3/candidates/plan/context/Git/downstream output.

The current 81 tests cover duplicate same-kind catalog and one compatible/
incompatible class scenario. Add independently equivalent builder/verifier
test methods/subtests for the missing required matrix:

1. exact semantic candidate id accepted; `reader`, `viral`, field-name token,
   prefix, suffix, case mutation and one-char near match rejected;
2. id present only in semantic `reason`/extra prose rejected; unsupported
   semantic schema, extra top-level key, extra decision key, wrong row type,
   invalid JSON/UTF-8, empty decisions and duplicate ids rejected;
3. registry exact heading accepted; malformed heading and body-only id rejected;
   duplicate registry singleton/catalog/heading rejected;
4. boundary exact unit/candidate/registry ref accepted; missing/foreign
   same-file target unit, duplicate unit/candidate across boundary files,
   injected extra top-level/unit/candidate/deferred key and prose-only id
   rejected;
5. closure exact deferred id accepted; nonempty unresolved blocking list,
   count/list inconsistency if field exists, prose-only id, extra key, empty
   catalog and duplicate closure singleton rejected;
6. compatible candidate corroboration semantic+boundary and compatible
   registry corroboration registry+boundary+closure stay accepted;
7. incompatible declaration-class collision stays rejected.

Use temporary identity-bound files conforming to real closed schemas. Clean
every file/root in `finally`. Assert exact builder/verifier error families; any
builder build-API failure also asserts destination absence.

Verification: py-compile; focused and four-module suites with exact count >81;
both real-v1 preflights; scoped diff-check; forbidden absence of real v2 config,
accepted-v4 input INVENTORY and all assignment probe/staging/candidate paths.

Terminal `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2_REREVIEW` only if all pass;
otherwise `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_FULL_MATRIX`.
