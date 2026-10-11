# Independent critic review: Viral Step 6A enforcement injection amendment

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6-source-reconstruction-step6a-enforcement-completion`
- Review kind: architecture/process
- Role/model/effort: independent critic, policy `gpt-5.5` / `medium`
- Actual platform model/effort: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `nri-independent-critic`
- Scoped override: none
- Independence declaration: I did not design, implement, remediate, execute QA for, or otherwise own the amendment or candidate under review.
- Timestamp: 2026-09-01T00:04:58+03:00
- Elapsed time: unavailable
- Token use: unavailable

## Scope

Reviewed `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_enforcement_injection_amendment_20260831.md` as a narrow amendment to the accepted enforcement-completion packet.

This review is limited to whether the amendment safely and implementably closes the executor stop without widening scope or adding a bypass. It does not authorize live `build`, live `remediate`, external-source access, network, MinerU, OCR, GPU/model execution, historical material, translation, candidate mutation, `MASTER_EN`, promotion, release, publication, staging, commit, or push.

## Identity and hash verification

Verified by read-only inspection and hashing:

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch: `codex/kb-creator-viral`
- HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Base enforcement packet: `56586563470FCA55B1CE31EB1EC73C71438B33A1FEBC1A1A39ADB8781AE3A604`
- Accepted base design review: `BFA0127AE82FF129A9E1CDA7B1FABEF7B5035ADFC8F64BCC672B24AB0E9F2D21`
- Intermediate blocked executor receipt: `E68DFB9658B2A9B70D77EC57F75FE1803D364E24F2323C8AC79150AF51F8E9B8`
- Injection amendment: `9C3864CA1A7836BEFB5D252BA1024075A26E171CB7A306D9653B7E266C0A6BA3`
- Live partial library: `C7974735159F35636011C5839561E466806807EB8599E4C11CCC6958E815C861`
- Live partial focused tests: `752CCCC1A74B1EA7ECE93B4D26FD82DB747D7962A93FFB56CC590754557BA796`
- Protected CLI: `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA`

Candidate manifests were recomputed with the project canonical record algorithm:

- all regular files: 502, `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA`
- inventory excluding only root `RECONSTRUCTED_EN.qa.json`: 501, `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766`
- protected subset excluding QA and `evidence/COMMANDS.json`: 500, `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`

I did not access the external Yandex locator. I did not run Git commands; branch and HEAD were verified by reading `.git` metadata files.

## Files checked

Read or materially inspected:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_enforcement_completion_packet_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_enforcement_completion_packet_review_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_enforcement_completion_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_enforcement_injection_amendment_20260831.md`
- `kb_creator/scripts/scenario_source_reconstruction.py`
- `kb_creator/tests/test_scenario_source_reconstruction.py`
- `kb_creator/scripts/reconstruct_scenario_source.py`
- Live candidate manifest evidence under `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`

Files changed:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_enforcement_injection_amendment_review_20260901.md`

No other durable file was intentionally changed.

## Assessment

The technical injection design is coherent in most respects:

- Public `build`, `preflight`, `remediate`, and `verify` signatures remain four-argument production entry points. The protected CLI exposes no profile/provider override surface.
- The proposed underscored test routes require a sealed `TEST` profile and profile-bound identity/filesystem providers, and the amendment explicitly forbids relaxed, skip, default-to-production, pytest-detection, or environment-variable bypasses.
- The Windows reparse classifier overlay is a legitimate way to exercise the `FILE_ATTRIBUTE_REPARSE_POINT` branch without requiring Developer Mode or Administrator privileges, provided the production reject function is shared and not bypassed.
- The 502-file hermetic bundle is large but implementable: it uses deterministic small bytes, a fake local source, fixture-local sidecar/contract/recovery, 124 pages/renders, 31 sheets, 204 assets with 112/92 reference split, 124 navigation anchors, current QA/COMMANDS shapes, and real 501-row inventory/hashes.
- The amendment correctly converts the earlier fake-count failure into executable requirements: 368 negative cases must perform one mutation, reseal only declared transport authorities, and assert exact earliest `ReconstructionStop.code`; three build cases must exercise real fresh-root, overwrite-refusal, and finalizer-parity behavior.
- The deterministic build writer proposal is a valid reusable seam in principle: no MinerU/OCR/network/model dependency, validated input model, fresh-root/refuse-existing, owned same-parent temp sibling, no-replace publication, deterministic non-QA ordering, `COMMANDS` then inventory/QA finalizer, and strict verification before publication.
- Candidate, CLI, QA, `COMMANDS.json`, source, sidecar, recovery, renders and protected orchestration documents remain protected by the amendment's technical rules.

However, the amendment has one process blocker.

## Findings

### P1 — Amendment authorizes in-place rewrite of an existing immutable executor receipt

Evidence:

- `docs/governance/nri_goal_governance.md` requires every non-exempt contributor receipt under `handoffs/` to be immutable and states that a correction supersedes a prior receipt; it does not rewrite it.
- The amendment declares scoped override `none`, then explicitly authorizes the existing blocked executor receipt to be replaced in place:
  - line 47: the existing `E68DF...` receipt may be replaced once;
  - lines 638-645: the same executor may perform an atomic same-path replacement of `luna_executor_viral_step6a_enforcement_completion_20260831.md`;
  - line 647: if code/tests changed and the result is blocked, the same replacement may record the new blocked state.
- That receipt is already hash-bound in this review task as `E68DFB9658B2A9B70D77EC57F75FE1803D364E24F2323C8AC79150AF51F8E9B8`, and the amendment itself uses that hash as evidence of the intermediate stop.

Impact:

Overwriting the existing receipt, even with a section that restates the prior blocked result, destroys the original immutable byte artifact and invalidates the governance model for contributor evidence. It also creates a precedent where a contributor can reclassify a completed handoff receipt as a mutable checkpoint after the fact without a recorded scoped governance override. That is a process/architecture blocker because the amendment is meant to close an evidence-integrity gap; it cannot do so by mutating already-bound evidence.

Required remediation:

Amend the packet before execution so that:

1. `luna_executor_viral_step6a_enforcement_completion_20260831.md` remains immutable at SHA-256 `E68DFB9658B2A9B70D77EC57F75FE1803D364E24F2323C8AC79150AF51F8E9B8`.
2. The resumed executor writes a new successor receipt path, for example `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_enforcement_completion_resume_20260901.md`, or another explicitly named new path.
3. The executor allowlist is updated to replace the old receipt path with that new receipt path, not add broad handoff write access.
4. The new receipt records `supersedes_intermediate_sha256=E68DFB9658B2A9B70D77EC57F75FE1803D364E24F2323C8AC79150AF51F8E9B8`, retains the prior stop evidence by reference and summary, and binds this amendment plus its accepted critic review.
5. Stop conditions require the original blocked receipt to remain byte-identical before and after execution.

This is a narrow process amendment. I did not identify a technical reason that the library/test injection design itself needs to be reopened if the receipt immutability issue is corrected.

## Recommendation

REJECT.

The amendment may not proceed to bounded executor implementation with the same-path receipt rewrite rule in place. Once the receipt rule is corrected to preserve the intermediate receipt immutably and write a new successor receipt, the rest of the amendment is suitable for execution without reopening the technical injection design, assuming all hashes and candidate manifests still match.

## Safe next gate

Orchestrator should request a one-point amendment that removes the same-path receipt rewrite and replaces it with a new successor receipt path plus immutable predecessor binding. After that amendment receives independent review with no open P0/P1, the executor may resume within the corrected three-path allowlist:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. the newly named successor executor receipt.

All live candidate files, QA, `COMMANDS.json`, CLI, source, sidecar, contract, recovery root, renders, plan/context/status/release/publication artifacts and Git state remain protected.

## P0/P1/P2 summary

- P0: none
- P1: in-place rewrite of the existing immutable executor receipt
- P2: none

## Forbidden actions declaration

I did not perform external-source access, network access, build/remediate execution, MinerU/OCR/GPU/model execution, history/translation access, candidate/source/sidecar/recovery/code/test/plan/context/status mutation, Git command, Git index/ref mutation, staging, commit, or push.

