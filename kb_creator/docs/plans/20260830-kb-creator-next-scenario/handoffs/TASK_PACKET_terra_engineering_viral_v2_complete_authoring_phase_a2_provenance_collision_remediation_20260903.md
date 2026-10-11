# Task packet — Viral v2 A2 structured decision provenance collision remediation

## Role and starting state

- Fresh `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Preserve unrelated/user edits; do not revert others.
- Blocking test-closure receipt SHA-256:
  `DAAEE694C9A4BECADD7B595467403D54907E572D444E145438FA8C245263F6F9`.
- Starting hashes:
  - builder `B50870D615BA590FFC4D5A6A5490085C2F91365ADAD0400277F915B692DD91AB`;
  - verifier `3733F6BF50F580FAACFFC7ADFAB33EBFD098F9AEFA580039F537223846177BA6`;
  - builder tests `4ADEC5AFDC5D6AEA5A5F41E7D8E9F814F4107D947251830B0BB2E9BFB8580A1F`;
  - verifier tests `4BC012362CA958DD507A0592CB47EDFD98BB0178F28E8ECF93EC06D74A45B451`.

## Ownership

Own the two MASTER_EN scripts, two focused test modules and one receipt
`terra_engineering_viral_v2_complete_authoring_phase_a2_provenance_collision_remediation_20260903.md`.
Do not edit prior receipts, helper/config/evidence/inputs/A3/candidates/plan/
context/Git/downstream output.

## Required provenance model

Replace flat `refs.update(ids)` with independently implemented provenance-aware
catalogs. Do not globally reject every cross-file repeat: production evidence
intentionally corroborates some exact ids across kinds.

Closed source roles and cardinality:

- at most one semantic-review-v2 catalog;
- at most one user-review registry Markdown catalog;
- at most one semantic-closure-v2 catalog;
- boundary-ledger-v1 may have multiple files (production has three), but its
  declared unit ids and candidate dispositions must be nonoverlapping across
  ledger files; repeated external registry refs are allowed corroboration.

Track declaration class per exact id:

- `candidate_decision`: semantic `decisions[*].candidate_id` and boundary
  `candidate_dispositions[*].candidate_id` may corroborate exactly;
- `registry_decision`: registry heading ids, boundary registry refs/deferred
  registry refs, and closure deferred ids may corroborate exactly;
- `boundary_unit_decision`: boundary `units[*].id` only; target-unit references
  resolve to same-file declarations but do not redeclare the id.

Reject:

- two files occupying any singleton catalog role;
- same exact id under incompatible declaration classes;
- duplicate semantic decisions, registry headings, closure ids, boundary unit
  declarations or boundary candidate dispositions;
- a boundary unit/candidate declaration repeated in another boundary file;
- target unit absent from the same boundary file;
- any common/prefix/near-match/free-text token as already specified.

Decision membership then uses exact id plus its valid declaration provenance;
do not accept reference-only target fields as declarations.

## Complete the test matrix

Retain the two currently failing collision tests and make them pass. Then finish
independently equivalent builder/verifier coverage for all four kinds and all
mutations from the preceding test-closure packet: valid exact ids, common,
prefix/suffix/case/near-match, prose-only, unsupported kind/schema/extra/wrong
shape/invalid UTF-8/JSON/empty, same-kind duplicate catalogs, compatible
cross-kind corroboration, incompatible cross-kind class collision, boundary
missing target unit/row injection, closure blocking inconsistency, malformed
registry/body-only id.

Every builder failure that uses a build API must assert destination absence.
Preserve every A1b/A2 count/hash/outcome/pending-A3/orphan/p123-p124 test.

## Verification

Capture exact counts (>77) and exits for py-compile, two-module focused suite,
four-module baseline, both real-v1 preflights and scoped diff-check. Confirm
real v2 config, accepted-v4 input INVENTORY and all assignment-created
probe/staging/candidate paths are absent.

Terminal:
`READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2_REREVIEW` only if everything passes;
otherwise `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_PROVENANCE_COLLISION`.
