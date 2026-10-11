# Task packet — Viral v2 Phase A2 P1 decision-ref remediation

## Role and finding

- Role: same `nri-engineer` / GPT-5.6-terra / medium owner.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- You are not alone in the worktree; preserve unrelated/user edits.
- Critic receipt:
  `gpt55_critic_viral_v2_complete_authoring_phase_a2_review_20260903.md`,
  SHA-256
  `37C5FD7B91140CB2AE566B0E634014764FCD23191DBD1BFA4E2654089C2297CC`.
- P1 reproduction: replacing decision refs with common token `reader` is
  accepted by builder and verifier because both tokenize arbitrary evidence
  text rather than extracting structured decision ids.

## Scope

Own only the two MASTER_EN scripts, their two focused test modules, and one new
receipt
`terra_engineering_viral_v2_complete_authoring_phase_a2_decision_ref_remediation_20260903.md`.
Do not edit prior receipts, helper/config, immutable evidence/inputs, A3,
candidates, plan/context, Git or downstream output.

## Required correction

Replace broad regex tokenization with independent closed structured-evidence
parsers. Extend each `migration.inputs.decision_evidence` row with one closed
evidence kind/extractor discriminator, and admit exact ids only from approved
fields of that kind. Reject unsupported kind, unsupported schema/version,
invalid UTF-8/JSON/Markdown shape, duplicate/conflicting ids, empty catalogs,
free prose and tokens outside the permitted fields.

Production evidence kinds must cover the actual approved inputs needed later:

- `kb_creator.semantic_unit_review.v2`: exact
  `decisions[*].candidate_id` values only;
- `kb_creator.viral_boundary_ledger.v1`: exact `units[*].id`,
  `units[*].registry_refs[*]`, `candidate_dispositions[*].candidate_id` and
  `candidate_dispositions[*].registry_ref` (if present), plus only other
  explicitly enumerated decision-id fields proven necessary by the schema;
- `kb_creator.semantic_unit_closure.v2`: exact ids in
  `deferred_nonblocking[*]`/other explicitly closed id arrays, not arbitrary
  strings elsewhere;
- the user-review registry Markdown: exact heading ids matching the closed
  registry heading grammar such as `### OUT-001 — ...`, `PROC-...`, `ENH-...`;
  no body-word tokenization;
- if critic/review receipts are bound as identity-only evidence, they must add
  no decision ids unless a separate closed receipt grammar explicitly names a
  machine-readable decision-id field.

For synthetic tests, use a miniature evidence file conforming to one of the
real closed schemas (prefer semantic review v2). Do not bind the frozen v1
config as decision evidence and do not use scenario id `viral` as a fake
decision. Use a specific exact id such as
`viral-logical_table-p020-l025` from an allowed field.

Builder and verifier must implement the parsers independently and must not
import each other. Exact equality only; no substring, prefix or case-folded
match.

## Tests

Add equivalent builder/verifier positive and negative tests for:

- exact valid structured decision id accepted;
- `reader`, `viral`, field names, schema tokens and common words rejected;
- exact-id prefix, suffix, case mutation and near-match rejected;
- id present only in a reason/body/free-text field rejected;
- unsupported evidence kind/schema/shape, invalid JSON/UTF-8 and empty catalog
  rejected;
- duplicate/conflicting ids and an unbound decision evidence file rejected;
- all existing six-ledger/count/hash/outcome/pending-A3/orphan/p123-p124 tests
  remain green.

Run py-compile, exact focused suite (now greater than 77 if tests are added),
four-module baseline, both real-v1 preflights and scoped diff-check. Confirm no
real v2 config, accepted-v4 input INVENTORY, probe/scratch/candidate remains.

Terminal line:
`READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2_REREVIEW` only if P1 is closed and
all checks pass; otherwise
`CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_DECISION_REF_REMEDIATION`.
