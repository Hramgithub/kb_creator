# Task packet — Viral v2 A2 structured decision-id test closure

## Role and takeover

- Fresh `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- You are not alone in the worktree. Preserve unrelated/user edits; do not
  revert others.
- Prior integration recovery receipt SHA-256:
  `216F029F5CDA287E23BCA501FD9C27C673E504A07A877389A1F0EEEA67C9F614`.
- Starting production hashes:
  - builder `B50870D615BA590FFC4D5A6A5490085C2F91365ADAD0400277F915B692DD91AB`;
  - verifier `3733F6BF50F580FAACFFC7ADFAB33EBFD098F9AEFA580039F537223846177BA6`.
- Starting tests:
  - builder `BD9B8234F6ADA84A7E339EEC9EF7A0AD1F8A00EB01C4A4DC8780B458FFA61B05`;
  - verifier `5C38DDBD0E3F6808598A97ADCA095A7F4F46ED9259900B6D788A235CE06206F9`.

## Ownership

Own the two focused test files and one new receipt
`terra_engineering_viral_v2_complete_authoring_phase_a2_decision_ref_test_closure_20260903.md`.
Treat the two production scripts as read-only unless a new test proves a
specific defect; if that occurs, stop and return `CHANGES_REQUIRED` with the
reproduction instead of editing production code. Do not edit prior receipts,
helper/config/evidence/inputs/A3/candidates/plan/context/Git/downstream output.

## Required independent test matrix

Add independently equivalent builder and verifier test methods for all four
closed evidence kinds:

- semantic review v2;
- user-review registry Markdown;
- boundary ledger v1;
- semantic closure v2.

For each implementation, exercise exact positive ids and mutations for:

- common refs `reader`, `viral`, schema/field-name tokens;
- prefix, suffix, case mutation and one-character near match;
- id present only in reason/body/evidence/scope/identity prose;
- unsupported kind/schema, extra top-level/row key, wrong row type, invalid
  JSON/UTF-8 and empty catalog;
- duplicate catalog ids and incompatible cross-file collision;
- boundary missing same-file target unit, unknown target unit, injected
  candidate/registry fields and deferred-row extra key;
- closure unresolved-blocking count/list inconsistency and prose-only id;
- registry malformed heading and body-only id.

Assert the exact expected builder/verifier error class/code and destination
absence where build APIs are used. Preserve all A1b/A2 count/hash/outcome/
pending-A3/orphan/excluded-page tests. The suite count must be greater than 77.

## Verification

Run and record exact counts/exits for:

1. py-compile of the two scripts and two tests;
2. focused two-module suite;
3. four-module baseline including visual QA and semantic proposer;
4. both real frozen-v1 builder/verifier preflights;
5. scoped `git diff --check`;
6. forbidden absence of real v2 config, accepted-v4 input INVENTORY, and all
   test/probe/staging/candidate paths created by this assignment.

Terminal line:
`READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2_REREVIEW` only if expanded tests
greater than 77 and all commands pass. Otherwise
`CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_TEST_CLOSURE` with exact defect.
