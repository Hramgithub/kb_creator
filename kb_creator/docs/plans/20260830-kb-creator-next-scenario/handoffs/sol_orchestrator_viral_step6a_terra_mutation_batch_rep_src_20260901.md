# Terra engineering assignment: Viral Step 6A REP and SRC mutation batch

This is sequencing under the already accepted architecture, not a design
amendment. No new architecture or critic review is required.

## Baseline and writes

- Library SHA-256:
  `EB3421D2205E1D54D4A7B4EA54BA7E09B7B8E057C704D8CED0D0748AA97CCB71`.
- Test SHA-256:
  `C345128969C76B9DB4FB5963866D0D44C07C9AFC9DDEAA9A1CF3D0394DF66A6F`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_rep_src_20260901.md` only.
- Everything else is read-only. No live, external, cache, Git or protected write.

## Implement exactly 20 cases

Read accepted packet sections 5.3, 7.3, 8.1 REP/SRC and 11. Implement:

- `REP-branch-wrong -> E_REPO_BRANCH`;
- `REP-head-wrong -> E_REPO_HEAD`;
- all exact 18 `SRC-*` ids/codes listed in section 8.1.

For every row, replace the shared COMMANDS proxy with a distinct callable that
mutates the real repository observation, source path/entry/bytes/hash/reparse,
or exact sidecar selector named by that id. Add the production verifier seam
that naturally emits the binding earliest code in the accepted phase order.

Implement the reusable `apply_case` / `reseal_transport` / `MutationAudit`
foundation for these rows: one semantic selector change, literal reseal tuple,
only allowed transport changes, one real `_test_verify` call, exact code,
uppercase selector hashes, zero outside reads/undeclared changes/residue. The
two reparse-related source cases use physical entries plus immutable
classification override and never privilege-skip.

Preserve every other family row and exact 371 collection; do not claim other
families complete. Use `python -B` and pytest `-p no:cacheprovider`. Run all 20
REP/SRC nodes, all three BLD smoke nodes and collection. Receipt includes the
20 canonical machine-readable audit rows/digest, commands, identities and
protected-surface evidence. Result is `COMPLETE_BATCH_PENDING_PHASE2_INTEGRATION`
only when all 20 pass; otherwise `BLOCKED` with exact remaining ids/symbols.
