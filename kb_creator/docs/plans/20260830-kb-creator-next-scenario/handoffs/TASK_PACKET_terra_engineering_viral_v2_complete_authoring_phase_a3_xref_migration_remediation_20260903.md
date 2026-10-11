# Task packet — Viral v2 A3 xref migration binding remediation

## Ownership

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Own only the two MASTER_EN production validators, their two focused tests and
  one receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a3_xref_migration_remediation_20260903.md`.
- Preserve unrelated edits. Do not touch plan/context, prior receipts, scratch,
  helper/config, candidates, immutable evidence, Git, MASTER_RU, Step 8A,
  HTML/PDF or production output.

## Bound defect

- Critic changes-required receipt SHA-256:
  `67BB38E33B7191D4061A6380A252ED9119A1931DFEF4273426D82616E520C6B7`.
- Public-path defect receipt SHA-256:
  `1C0A0A84C42B686C778D595A445995D78E5DEDEB15A30F46F11A4BA6C576188B`.
- Starting builder SHA-256:
  `5984748E8591EBD6CA2E94CBD1D7DE8528C8E2126D2BD1D9C22DBAD725441673`.
- Starting verifier SHA-256:
  `2824437D111E78B1DFC259EEB0C356866978F0F013FBE2B2AD375C126523A0B1`.
- Starting builder-test SHA-256:
  `1C09E5EE3922EF4826D2ED69FF673E06885CD22F2EFE17B0623F91EF5330E136`.
- Starting verifier-test SHA-256:
  `64F72B68F89202D39B6FEB4E45FE1D7C4E65EDDA44DB7C1B3C3A6DE853D76876`.

Refuse on hash drift. Read both receipts and architecture before editing.

## Required remediation

In builder and independently in verifier, bind each xref
`migration_row_id` to the exact materialized migration target for that xref,
not merely any nonempty string or any unrelated declared target. The valid
identity is the closed `xrefs:<xref_id>` target represented by the approved
migration ledger/new-reviewed-target closure. Reject drift, another real xref's
target, wrong domain, unknown target, duplicate reuse and any mismatch between
xref declaration and migration materialization. Do not weaken A2 migration
membership, decision-reference or target closure.

Audit the analogous hierarchy `migration_row_id` validation while here. If a
public one-field drift probe is accepted, close it independently with exact
`hierarchy:<anchor>` identity and test it; otherwise record the passing audit
without changing unrelated behavior.

Keep the existing builder public defect test and mirror it through verifier's
public top-level path. Add positive tests proving full A3 xrefs pass top-level
builder and verifier. All builder negatives assert destination absence.

## Verification

Run py-compile, the direct defect tests, full focused suite, exact normal and
reverse four-module baselines, both frozen-v1 preflights, scoped diff check,
hashes and forbidden-output checks. No real v2 config/candidate/accepted-v4
inventory or new scratch may remain; do not mutate the six pre-existing
`.v2-inputs-*` roots.

Receipt records exact commands/counts/hashes. End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A3_TEST_CLOSURE_RETRY`, or
- `PARTIAL_V2_COMPLETE_AUTHORING_PHASE_A3_XREF_MIGRATION_REMEDIATION`.
