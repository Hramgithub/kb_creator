# Task packet: Viral v2 Phase A1b recovery

## Role / takeover

- Fresh `nri-engineer` (`gpt-5.6-terra`, medium) takes over after prior bounded
  owner exhaustion.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- You are not alone. Preserve the four exact current hashes recorded in
  `context.md` as your starting point; do not revert partial validated work.

Exclusive paths:

- builder, verifier and their two test modules;
- receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a1b_recovery_20260903.md`.

## Exact remaining scope

1. Complete verifier parity for UTF-8 byte-boundary, exact decoded prefix/
   substring character offsets and `raw_text_sha256`.
2. Define and validate closed `eol_profile` in both implementations with exact
   raw counts for LF, CRLF, CRCRLF, lone CR, line slots and nonblank line slots;
   return/recompute aggregate page/byte/line/nonblank/EOL metrics.
3. Review both existing validators for exact pages 1..122, canonical path/page
   binding, safe paths, unique ids/order, scalar bool rejection, allowed enums,
   BOM/UTF-8, raw hash, adjacency and full coverage; close any actual gap.
4. Add dedicated builder and independent-verifier tests: positive tiny/122-page
   fixture, missing nonblank byte, missing blank/EOL byte, overlap/reorder,
   duplicate id, wrong path/page, raw/text hash, char offsets/UTF-8 boundary,
   enum and EOL profile. Keep them compact and deterministic.
5. Run py_compile, both focused modules, four-module baseline and both real v1
   preflights. Confirm no config/helper/candidate/input inventory/Git mutation.

Do not implement A2 migration, A3 event provenance/payload/hierarchy or edit
helper/config/candidates. Return `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2`
only if A1b is fully wired/tested; otherwise a precise blocker. Include hashes,
counts and receipt SHA.
