# Independent critic review: Viral Step 6A QA metadata-integrity remediation

- Goal: `20260830-kb-creator-next-scenario`
- Step: Viral Step 6A reconstruction-builder QA metadata-integrity remediation
- Review kind: implementation/process, release-style boundary review
- Role/model/effort: independent critic, policy `gpt-5.5` / `medium`
- Actual platform model/effort: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `nri-independent-critic`
- Scoped override: none
- Independence declaration: I did not implement, design, remediate, execute QA for, or otherwise own the candidate under review.
- Timestamp: 2026-08-31T23:05:37+03:00
- Elapsed time: unavailable
- Token use: unavailable

## Scope

Reviewed the completed metadata-integrity remediation for the existing candidate root:

`kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`

This review is limited to the Step 6A reconstruction-builder/remediation boundary. It does not authorize `MASTER_EN`, semantic acceptance, release, publication, historical translation use, external-source access, MinerU/OCR/GPU/model execution, rebuild, promotion, staging, commit or push.

## Candidate and authority identity

Required worktree and revision were verified by read-only `.git` metadata file inspection, not by invoking Git:

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch: `codex/kb-creator-viral`
- HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`

Authority/evidence hashes independently verified:

- Base remediation packet: `C86335AFCAC0A6060BA8E9D616172115905DE7B08F3ED1E88BCB822D6CE8B648`
- One-point amendment: `9FDBC4848AAF280DDFE4080E1263B4146320436E5A832A296C50209AB9B99292`
- Accepted amendment review: `DB93AE31E552C2C5A46EAD52D9EE5D620625B6344C7DDE3D5B144E1056A4512F`
- Prior implementation/process reject receipt: `AE14A9D917FE9BAB4BD64DD1BAE84F6B3A52209D1A38D5483389E022BE69CF9B`
- Executor receipt: `27E462EBFCDA9126700BEE3CB958595C64823A3386AF55EC66AF277AD08CE645`
- Bounded QA receipt: `D40C265B9272A0F2BD44ADC95CDD152B32B4C6EB69CD3E561D817C07549BBDB7`
- Prior visual QA correction receipt: `194BF7EE471FF7E7DF859ED7958F7B3978F0F6C54536136C26CC6C6D1A7765DD`
- Local source PDF: 20,718,150 bytes, SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`
- Source admission sidecar: `3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9`

I did not access the external Yandex locator.

## Files checked

Read fully or inspected materially:

- `D:\NRI\AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_qa_metadata_integrity_remediation_packet_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_qa_metadata_integrity_remediation_packet_amendment_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_packet_review_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_packet_amendment_review_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_qa_metadata_integrity_remediation_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_qa_metadata_integrity_remediation_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_reconstruction_builder_qa_retry_correction_20260831.md`
- `kb_creator/scripts/scenario_source_reconstruction.py`
- `kb_creator/tests/test_scenario_source_reconstruction.py`
- Live candidate `RECONSTRUCTED_EN.qa.json`
- Live candidate `evidence/COMMANDS.json`
- Live candidate evidence/render/page/asset inventory by read-only enumeration
- Source PDF and source admission sidecar by read-only hashing

Files changed:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_review_20260831.md`

No other durable file was intentionally changed. No Git staging, commit, push, reset, checkout or other Git command was performed.

## Verification performed

Read-only verification found that the candidate data is now internally consistent on the main metadata points:

- Full candidate manifest: 502 regular files, SHA-256 `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA`
- Inventory excluding only root `RECONSTRUCTED_EN.qa.json`: 501 rows, SHA-256 `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766`
- Protected subset excluding QA and `evidence/COMMANDS.json`: 500 rows, SHA-256 `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`
- Render/contact-sheet manifests remain bound to the visual carry-forward evidence:
  - 155 renders/contact sheets: `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A`
  - 124 source renders: `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C`
  - 31 contact sheets: `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A`
- `RECONSTRUCTED_EN.qa.json` now uses schema `kb_creator.reconstructed_en_qa.v3`, state `candidate_needs_review`, recovery manifest/evidence hashes `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169` / `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC`, `open_blocker_count=4`, 501-row inventory, and expected counts for 124 pages, 31 sheets, 204 assets, 112 referenced assets, 92 unreferenced assets, 39 handouts, 7 maps, 13 pregens and 124 anchors.
- `evidence/COMMANDS.json` now uses schema `kb_creator.reconstruction_commands.v3`, state `candidate_needs_review`, actions `preflight`, `remediate`, `contact_sheets`, `verify`, local source path `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`, and false values for `build_invoked`, `mineru_invoked`, `ocr_invoked`, `gpu_or_model_invoked`, `network_invoked` and `external_source_used`.
- The 501-row inventory is non-circular: it includes `evidence/COMMANDS.json` and excludes only root `RECONSTRUCTED_EN.qa.json`.
- No forbidden candidate payload class was found in the read-only inventory scan for `.pdf`, `.pyc`, `__pycache__`, `_bridge_runtime` or cache paths.

I did not run the live CLI `verify` command because `kb_creator/scripts/scenario_source_reconstruction.py:32` invokes `git rev-parse --show-toplevel`, and this review packet forbids Git operations by the critic. I inspected the live verifier source and the executor/QA receipts instead.

## Findings

### P1 — Strict verifier and focused tests do not fully implement the accepted packet's enforcement layer

Evidence:

- The accepted packet explicitly requires `verify()` to fail before success on branch/HEAD, forbidden PDF/cache/runtime/`.pyc` classes, exact evidence schemas, source/recovery/contract/ledger/QA/commands/count/hash relationships, 501 unique inventory rows, command policy, all command-evidence render/sheet hashes and mappings, and state/semantic flags. See packet lines 184-198 and acceptance lines 279-285.
- The accepted packet also requires hermetic tests for a broad negative mutation matrix, with isolated mutations for stale source/recovery/contract hashes, stale QA schema/state/count/gates, stale blocker ledger, missing/extra/stale/duplicate inventory rows, wrong bytes/hash/digest/order/path forms, missing evidence/contact-sheet files, command policy violations, repeat-remediate refusal and the observed live P1 symptoms. See packet lines 218-244.
- The live Step 6A test file contains only eight test functions:
  - `test_role_partition_is_exact`
  - `test_role_partition_rejects_gap`
  - `test_inventory_excludes_only_qa_and_is_deterministic`
  - `test_invalid_inventory_path_and_reparse_are_rejected`
  - `test_json_is_sorted_utf8_lf_final`
  - `test_cli_module_remains_recovery_only`
  - `test_amended_baseline_constant_is_post_remediation`
  - `test_required_false_policy_is_explicit`
- Those tests are mostly helper/static checks. They do not construct a complete hermetic valid bundle and mutate it through the named negative matrix, and they do not reproduce each prior live P1 symptom before the fix.
- The live verifier in `kb_creator/scripts/scenario_source_reconstruction.py:115-138` checks source, recovery, topology, selected schemas/cardinalities, QA recovery/open-blocker/inventory binding, command action set, contact-sheet file hashes, command false flags/source path, and page markdown/render hashes. It does not itself check branch/HEAD; branch/HEAD are only in `preflight()` at lines 102-107. It also does not validate the full named packet matrix, including all command-evidence render-page hashes/mappings, command counts versus live evidence, navigation prev/next/link integrity, inventory uniqueness beyond equality to the reconstructed list, all QA gate/scalar fields, or explicit forbidden payload classes beyond what happens indirectly through fixed cardinality/topology.

Impact:

The first prior P1, stale QA/recovery/source/ledger/inventory metadata, appears materially corrected in the live candidate. The second prior P1, missing enforcement layer, is only partially corrected. The current `verify()` and focused tests can catch the original stale QA inventory class, but they do not satisfy the accepted packet's full fail-closed verifier and negative-test contract. That leaves acceptance dependent on ad hoc receipt assertions rather than the durable enforcement layer that the packet made a release-style prerequisite.

Required remediation:

Before this boundary can advance, update the implementation and tests within a new explicitly authorized packet or executor task so that:

1. `verify()` either directly enforces all packet-listed mismatch classes or the packet is amended to a narrower, honest verifier contract before implementation review.
2. Branch/HEAD handling is made unambiguous: either `verify()` includes the branch/HEAD gate required by the packet, or the architecture is amended to state that branch/HEAD are preflight-only and strict verification is scoped accordingly.
3. The focused test file includes a hermetic complete positive bundle and isolated negative mutations for the named packet classes, including the two prior live P1 symptom families.
4. The test evidence distinguishes full-suite count from Step 6A-specific enforcement coverage, rather than treating 127 total passing tests as proof of the Step 6A negative matrix.

### P2 — `build()` behavior no longer matches the accepted packet's stated preservation model

Evidence:

- The accepted packet states that `build()` remains fresh-root/refuse-overwrite, is not run in this remediation, and must use the shared finalizer after every non-QA artifact for that builder stage has been written. See packet line 143.
- The live implementation replaces `build()` with unconditional refusal: `def build(*args:Any,**kwargs:Any)->dict[str,Any]:raise ReconstructionStop("build is not authorized in metadata remediation")` at `kb_creator/scripts/scenario_source_reconstruction.py:139`.

Impact:

This does not by itself prove candidate metadata corruption, and no build is authorized for this remediation. However, it is a scope drift from the accepted packet: the remediation disables the generic builder entry point instead of preserving its fresh-root behavior with the shared QA finalizer. This should be corrected or explicitly re-authorized before future work depends on this library as a reusable reconstruction builder.

Required remediation:

Either restore the packet-stated fresh-root/refuse-overwrite `build()` behavior with the shared finalizer in a separate authorized slice, or amend the architecture to make this library a metadata-remediation-only verifier/finalizer and provide a different explicitly authorized builder path.

## P1 disposition

- Prior P1: stale QA/recovery/source/ledger/inventory metadata — closed on data evidence. The candidate now has QA v3, current recovery bindings, four open blockers, truthful 501-row inventory, and local-source-only command policy.
- Prior P1: missing fail-closed enforcement layer — not fully closed. The live verifier and tests are materially narrower than the accepted packet and do not implement the required negative mutation matrix.

## Remaining required blockers

The following candidate blockers remain intentionally open and must not be treated as closed by this review:

- `candidate_needs_review`
- semantic/reading-order correctness
- visual placement/layout fidelity beyond the carried-forward 67/67 sheet inspection
- asset ownership/usage uncertainty and broader human semantic review

## Recommendation

REJECT for Step 6A reconstruction-builder/remediation boundary advancement.

The metadata remediation data appears correct, but material implementation may not advance to the next Step 6 semantic review boundary until the open P1 enforcement-layer gap is resolved or the architecture is amended and re-reviewed. This review does not authorize `MASTER_EN`, final acceptance, release, publication, Git mutation, external-source access, MinerU/OCR/model/network execution or rebuild.

## Next action

Orchestrator should request a narrow remediation packet or amendment for the enforcement-layer gap. The next packet should either implement the original strict verifier/negative-mutation matrix as written, or honestly narrow the required verifier/test contract and explain why the narrower contract is sufficient for this already-built candidate while preserving `candidate_needs_review`.

