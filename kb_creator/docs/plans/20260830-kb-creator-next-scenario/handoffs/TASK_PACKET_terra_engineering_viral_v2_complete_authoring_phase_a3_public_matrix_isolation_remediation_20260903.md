# Task packet — Viral v2 A3 public-matrix isolation remediation

## Fixed scope

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Own only the two focused test modules and one receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a3_public_matrix_isolation_remediation_20260903.md`.
- Both production validators are fixed and must not be edited.
- Preserve unrelated edits. Do not touch plan/context, prior receipts, scratch,
  helper/config, candidates, inputs, Git, MASTER_RU, Step 8A, HTML/PDF/output.

## Bound state and reproduced failure

- Invalid verifier-closure receipt SHA-256:
  `16FCFB836A934864028ACE759953DBFD07E740236A104EC1826A6067DC4EEFF3`.
- Builder SHA-256:
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`.
- Verifier SHA-256:
  `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.
- Starting builder tests:
  `D7ADB3EC1BC1E38C37B1662F4FA067D2FF9B8564B66670EBBF6EDCFFF63ED965`.
- Starting verifier tests:
  `54E68128A564971B3E03B7E0C8D75E704C173BBF66DD59CD308B7AC319C38E65`.
- Orchestrator exact four-module run on those bytes:
  `Ran 104 tests in 66.851s`, `FAILED (failures=39, errors=26)`.

Major reproduced symptoms:

- numerous legacy builder positives fail after public tests with
  `v2 asset event owner mismatch`, proving shared fixture mutation/order leak;
- serializer positive fails `v2 equipment boundary mismatch`;
- recovery/decision/migration positives are preempted by mutated asset events;
- verifier typed omission cases correctly reject at top-level
  `E_C2B_SCHEMA: v2-typed-payload` but tests falsely require only
  `E_V2_(STRUCTURE|PAYLOAD)`;
- verifier extra authorial leaf rejects `E_V2_PAYLOAD: unbound` while tests
  falsely require only `E_V2_STRUCTURE`;
- missing pair assets reaches `E_V2_PAYLOAD: pointer` while expectation omits
  payload.

Refuse on production hash drift.

## Required remediation

Make every public-matrix test and helper create an independent deep fixture.
No mutation may survive a subTest or test method. Eliminate module/class/global
mutable aliases, shallow-copy nested values and shared temp input mutation.
Each mutation starts from a freshly validated positive config.

Restore all legacy positives without weakening production. For every negative,
assert the exact legitimate first failing seam. Closed-schema omission may
expect the closed top-level schema code; invented/unbound leaves may expect
payload closure; do not use a catch-all regex that would let an unrelated early
error pass. Preserve explicit public rejection of every critic probe and
builder destination absence.

Run these in separate fresh processes and require all pass:

1. builder module alone twice;
2. verifier module alone twice;
3. focused builder then verifier twice;
4. focused verifier then builder twice;
5. normal four-module twice;
6. reverse four-module twice.

Also run py-compile, both frozen-v1 preflights, scoped diff, production hash
recheck and forbidden-output/scratch checks. Loader count must remain at least
104 and coverage may not be removed or hidden from discovery.

End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A3_REREVIEW`, or
- `PRODUCTION_DEFECT_V2_COMPLETE_AUTHORING_PHASE_A3_ISOLATION_REMEDIATION` with
  minimal proof and no production edit.
