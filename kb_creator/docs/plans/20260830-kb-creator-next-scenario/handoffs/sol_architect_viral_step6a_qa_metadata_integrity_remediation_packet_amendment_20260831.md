# Viral Step 6A QA metadata-integrity packet: immutable orchestration-state amendment

## Amendment metadata

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-qa-metadata-integrity-remediation-amendment`.
- Result: `amendment_ready_for_independent_review`; execution remains forbidden.
- Architecture/root-cause role: `gpt-5.6-sol`, requested `high`; actual platform model/effort `unavailable`, assignment state `user-directed / platform-unverified`.
- Orchestrator policy owner: main chat `gpt-5.6-sol`, `medium`; scoped override `none`.
- Original immutable packet: `sol_architect_viral_step6a_qa_metadata_integrity_remediation_packet_20260831.md`, SHA-256 `C86335AFCAC0A6060BA8E9D616172115905DE7B08F3ED1E88BCB822D6CE8B648`.
- Independent critic rejection: `gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_packet_review_20260831.md`, SHA-256 `DF582DC2D3C65BC73679E2F41C29C231E9C853C629886AE4AA0585EBB86F958B`.
- Critic finding addressed: one P1; no P0 or P2.
- Token use: `unavailable`.

This amendment is additive and immutable. It does not edit the original packet or critic receipt and confers no implementation authority.

## Sole defect and sole supersession

The original packet incorrectly made the then-current SHA-256 values of orchestrator-owned `plan.md` and `context.md` fail-closed executor admission inputs. Those canonical documents legitimately change when the main-chat orchestrator integrates reviews, records the active owner or updates the next action. Their normal governance evolution must not invalidate an otherwise unchanged candidate remediation baseline.

This amendment supersedes **only** the following original-packet requirements:

1. In `Admitted immutable baseline` / `Repository and source bindings`, delete the row that prescribes exact SHA-256 values for `canonical plan / context`. No replacement fixed hash is prescribed.
2. Anywhere the packet's executor pre-write admission could be read to include those two listed plan/context SHA values through a collective phrase such as `bindings above`, exclude plan/context from that fixed-value admission set.
3. In `Mutation audit and required receipts`, replace the requirement to bind plan/context to packet-era hashes with the dispatch-time protected-document audit defined below.

The original acceptance criterion that no plan/context/status mutation occurred is retained and clarified: it is proved by executor-window pre/post equality, not by equality to an earlier architecture-task snapshot.

## Replacement orchestration-document rule

`plan.md`, `context.md`, `kb_creator/PROJECT_STATUS.md`, `kb_creator/README.md`, `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`, applicable release/status/README artifacts, and every pre-existing orchestration handoff other than the one newly authorized executor receipt remain protected read-only.

Immediately after the orchestrator has integrated the accepted amendment review and immediately before the executor's first material write, the executor captures for every protected orchestration document in scope:

- exact relative path and existence;
- raw byte length; and
- raw-byte SHA-256.

Immediately after execution, it captures the same set again. The path set, existence, byte lengths and SHA-256 values must be identical pre/post. The newly authorized executor receipt is the sole allowed orchestration-path addition and is excluded from the equality set. No protected orchestration document may be created, deleted, renamed, normalized or rewritten by the executor.

The dispatch-time values are mutation-audit evidence only. They are not prescribed by this packet/amendment, are not compared with the superseded packet-era plan/context hashes, and may legitimately differ between amendment review integration and executor dispatch. If any protected orchestration document changes after the executor takes its pre-write snapshot, the executor stops and reports the concurrent/protected-path delta; it must not overwrite, restore or absorb that change.

Only the main-chat orchestrator may edit canonical plan/context/status. This amendment grants the executor no orchestration ownership.

## Bindings preserved fail-closed

Every other original-packet binding and control remains unchanged and fail-closed, including:

- original packet SHA-256 `C86335AFCAC0A6060BA8E9D616172115905DE7B08F3ED1E88BCB822D6CE8B648`;
- critic rejection SHA-256 `DF582DC2D3C65BC73679E2F41C29C231E9C853C629886AE4AA0585EBB86F958B` and, after acceptance, the detached SHA-256 of the fresh amendment-review receipt supplied at dispatch;
- branch/HEAD, local source PDF, admission sidecar, contract source/snapshot, recovery root/manifest/evidence and prior visual-QA bindings;
- candidate 502/501/500 manifests, 155/124/31 render manifests, protected candidate files and both mutable candidate-file baseline hashes;
- shared-library and focused-test baseline hashes, with the CLI remaining protected;
- exact mutable allowlist, inventory rule and cardinality, schemas, builder/remediate/verify semantics, local-source policy, focused tests and negative mutation matrix;
- exact runtime commands, post-manifest algorithm, visual-QA carry-forward conditions, acceptance criteria and executor stop conditions; and
- `candidate_needs_review`, all semantic/reading-order/placement/ownership uncertainty, no rebuild/MinerU/OCR/external-source access/Git mutation/promotion/publication boundaries.

No allowlist path is added or removed. No inventory, test, command, stop condition or implementation scope is changed by this amendment.

## Concise acceptance delta

A fresh independent critic may accept this amendment when it confirms all of the following:

1. exact plan/context SHA values are no longer executor admission requirements;
2. plan/context/status/README and other orchestration documents remain protected read-only through dispatch-time pre/post equality evidence;
3. the executor cannot treat normal pre-dispatch orchestrator updates as a candidate-baseline failure;
4. any orchestration-document change during the executor window still fails closed; and
5. every non-orchestration technical binding and every other original-packet rule remains unchanged.

Acceptance of this amendment authorizes neither execution nor Step 6A acceptance by itself. The next gate is a fresh independent `gpt-5.5`, `medium` amendment review written only to:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_packet_amendment_review_20260831.md`

Only after that review returns no unresolved P0/P1 and the orchestrator integrates it may the already-specified bounded executor be dispatched. Separate bounded QA and fresh independent implementation/process review remain mandatory afterward.

## Amendment-task mutation audit

This architecture task writes only this amendment. The original packet, critic receipt, code, tests, CLI, candidate, source, sidecar, contract, recovery root, render evidence, plan, context, status, README, prior receipts and Git state are read-only. No build, remediate, verify, external source, MinerU/OCR, network, Git mutation or publication action is performed.
