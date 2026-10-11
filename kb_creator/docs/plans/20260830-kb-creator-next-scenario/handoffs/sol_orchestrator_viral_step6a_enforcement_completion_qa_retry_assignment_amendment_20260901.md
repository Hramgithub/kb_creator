# Viral Step 6A QA retry assignment-record amendment

- Goal / step: `20260830-kb-creator-next-scenario` /
  `6A-enforcement-completion-qa-retry-assignment-correction`
- Owner: main-chat orchestrator, `gpt-5.6-sol` / `medium`
- Status: authorized one-point receipt correction only

## Trigger

The immutable QA retry receipt
`luna_qa_viral_step6a_enforcement_completion_retry_20260901.md`, SHA-256
`A16ACCE6E49F9CB520432C1BAC21F48D3DF9DE2EF773C460DF1D1900944CC1B2`,
correctly records the technical evidence and `PASS`, but its header contains a
false assignment-topology statement:

> `Assignment state: user-authorized fresh UI-visible QA retry; completed.`

The task was not UI-visible. The user explicitly requested that the retry be
delegated to an internal QA subagent. The orchestrator therefore spawned the
internal `nri-qa` subagent `/root/viral_step6a_qa_retry`. This is a bounded
user-authorized scoped override of the earlier restriction that internal agents
be used only for the critic.

## Immutability and exact correction

The predecessor receipt remains byte-immutable at the hash above. The same QA
subagent may write exactly one absent-before correction receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_enforcement_completion_retry_assignment_correction_20260901.md`

The correction receipt must:

1. cite this amendment and the immutable predecessor receipt/hash;
2. supersede only the assignment-topology, assignment-state and scoped-override
   statements;
3. record the factual topology as internal `nri-qa` subagent
   `/root/viral_step6a_qa_retry`, requested by the user;
4. record actual platform model/effort as `unavailable` unless independently
   exposed, while retaining the policy request `gpt-5.6-luna / high`;
5. record assignment state as `platform-unverified` and scoped override as
   `user authorized this bounded internal QA subagent, superseding the earlier
   critic-only internal-agent restriction for this retry only`;
6. affirm that every technical command, hash, count, finding, PASS boundary and
   probe-cleanup statement in the predecessor remains unchanged;
7. perform no test rerun, probe creation, candidate/source/code/test/prior
   receipt/plan/context/Git mutation or other write.

No UI task may be claimed, created or archived for this correction. The only
new write authorized by this amendment is the correction receipt itself.
After its hash is captured, the main-chat orchestrator may integrate the QA
result and dispatch the internal independent `gpt-5.5` critic review.
