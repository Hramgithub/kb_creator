# Independent critic design review: Viral Step 6A QA metadata-integrity remediation packet

## Receipt metadata

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6-source-reconstruction-step6a-qa-metadata-integrity-remediation`
- Review kind: architecture/process design review
- Role/model/effort requested: fresh independent critic, `gpt-5.5`, medium
- Actual platform model/effort: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol`, medium
- Assignment state: `nri-independent-critic`
- Scoped override: none
- Independence declaration: I did not implement, materially design, remediate, execute, or QA the remediation packet or candidate under review.
- Timestamp: 2026-08-31T22:40:30+03:00
- Elapsed time: unavailable until runtime goal completion metadata
- Token use: unavailable until runtime goal completion metadata
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`, verified by read-only Git metadata file inspection, not by invoking Git

## Verdict

REJECT.

The packet correctly targets the two prior P1 defect classes and is otherwise a strong narrow remediation design, but it introduces a new P1 blocker by binding exact hashes for orchestrator-owned mutable `plan.md` and `context.md`. Those hashes already differ in the live worktree before this review receipt is integrated. A correct executor would have to stop before writing, while ignoring the mismatch would bypass the packet's own fail-closed admission model.

## Candidate identity and bindings checked

Reviewed packet:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_qa_metadata_integrity_remediation_packet_20260831.md`
- Expected SHA-256: `C86335AFCAC0A6060BA8E9D616172115905DE7B08F3ED1E88BCB822D6CE8B648`
- Observed SHA-256: `C86335AFCAC0A6060BA8E9D616172115905DE7B08F3ED1E88BCB822D6CE8B648`
- Hash result: pass

Prior receipt bindings:

- Prior independent reject receipt `gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_review_20260831.md`: `AE14A9D917FE9BAB4BD64DD1BAE84F6B3A52209D1A38D5483389E022BE69CF9B`
- Corrected QA receipt `luna_qa_viral_step6a_reconstruction_builder_qa_retry_correction_20260831.md`: `194BF7EE471FF7E7DF859ED7958F7B3978F0F6C54536136C26CC6C6D1A7765DD`

Local runtime source:

- `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`
- Bytes: `20,718,150`
- SHA-256: `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`
- Admission sidecar: `kb_creator/working/viral/source/SOURCE_ADMISSION.json`
- Sidecar SHA-256: `3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9`
- Sidecar policy fields checked: `runtime_dependency=false`, `external_path_allowed_after_admission=false`, `subsequent_source_path=kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`, `generated_origin_pdf_is_source=false`
- External Yandex locator: not accessed; treated only as provenance data inside the sidecar

Live packet baseline claims independently reproduced:

- Candidate all regular files: `502`, manifest `52E44F725AB121EC61A255B747EA467B4371481F391EB5E79B51132E67258066`
- Candidate all files except `RECONSTRUCTED_EN.qa.json`: `501`, manifest `2FF3FBE3D56E3F8FF3720203267776DB97A738136861A4E72140F3D4286B9592`
- Protected candidate subset excluding QA and `evidence/COMMANDS.json`: `500`, manifest `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`
- All `renders/` files: `155`, manifest `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A`
- `renders/source/`: `124`, manifest `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C`
- `renders/contact_sheets/`: `31`, manifest `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A`
- Recovery root all regular files: `211`, manifest `03E50B77DB3F4472F1650EF913F9F7EC4510ACEC59072670384B516336ACD258`
- `SOURCE_IDENTITY.json`: `276430E8AFC7C8310421D661F9753F0DB4AFBD1091D9B0B9C34084BB2BE438AC`
- `evidence/BLOCKER_LEDGER.json`: `CD20D4137CF2FFA717DD36FC3D4ED433340D5886C59ABD355658C4F7BD475101`
- `RECONSTRUCTED_EN.md`: `259B25D61D9BBFBB6314411DD73B257B56ECDFD8480B6E3EAD3DBCCA35DB5601`
- Mutable baselines:
  - `RECONSTRUCTED_EN.qa.json`: `FE142A0C8749B0D139265659A08F88F6CB67B3D34EB9815DB2B62875FA6B75DE`
  - `evidence/COMMANDS.json`: `EBD21CE0EB5EAC0986D7C4D1EABA3B9B24267858F495CEB38BF08F25FEE1DC07`
- Contract source `kb_creator/contracts/viral.json`: `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`

Canonical plan/context live hashes:

- Packet-required `plan.md`: `10957DC755651C423D03FB0995EF02E122F34761EC7973D800DD0081325F07A7`
- Live observed `plan.md`: `4D664C9F8F723C7FB56B52E2A1291EFBBF7821A21C7A197AEC2AF3046859C16B`
- Packet-required `context.md`: `79E2C0879285D7334F280ECB3CB366E0B1A5ABA2EF7DD8929D763C14D4194F9C`
- Live observed `context.md`: `F321596E754F7DD0928F557042B5736CB51BA7310DE2D7961BBD191E146F3398`

## Files checked

Read fully or inspected read-only:

- `D:\NRI\AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_qa_metadata_integrity_remediation_packet_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_review_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_reconstruction_builder_qa_retry_correction_20260831.md`
- `kb_creator/working/viral/source/SOURCE_ADMISSION.json`
- `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`
- `kb_creator/scripts/scenario_source_reconstruction.py`
- `kb_creator/scripts/reconstruct_scenario_source.py`
- `kb_creator/tests/test_scenario_source_reconstruction.py`
- Live candidate manifests and selected candidate JSON evidence under `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`

Changed files:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_packet_review_20260831.md`

Forbidden actions not performed: no external source access, no network, no build/remediate, no MinerU/OCR, no GPU/model, no translation/history access, no packet/code/test/candidate/source/sidecar/plan/context mutation, no Git command, no Git index/ref/commit/push mutation.

## Findings

### P0

None.

### P1

1. The packet over-binds orchestrator-owned canonical `plan.md` and `context.md` hashes, making execution fail-closed before it can start.

   Evidence:

   - The packet's repository/source binding table requires exact canonical plan/context hashes `10957DC755651C423D03FB0995EF02E122F34761EC7973D800DD0081325F07A7` and `79E2C0879285D7334F280ECB3CB366E0B1A5ABA2EF7DD8929D763C14D4194F9C`.
   - Live read-only hashing during this review observed `plan.md` as `4D664C9F8F723C7FB56B52E2A1291EFBBF7821A21C7A197AEC2AF3046859C16B` and `context.md` as `F321596E754F7DD0928F557042B5736CB51BA7310DE2D7961BBD191E146F3398`.
   - NRI governance makes `plan.md` and `context.md` main-chat orchestrator-owned canonical state. They are expected to change when the orchestrator captures this review, updates active owner/next action, or records recovery state.
   - The packet's stop conditions require stopping before first write on packet/review and baseline mismatches. Therefore, a correct executor would stop on live plan/context hash drift, while proceeding would require bypassing the packet's own admission table.

   Why this blocks:

   The packet is meant to be a narrow in-place remediation for candidate QA metadata. Binding exact hashes of mutable orchestration files couples executor admission to normal orchestrator bookkeeping and creates a false blocker unrelated to candidate safety. The packet should prevent executor mutation of plan/context, not require that their pre-review hashes remain frozen across review integration.

   Required remediation:

   Issue a corrected immutable packet or amendment that:

   - removes exact `plan.md` and `context.md` hashes from executor pre-write admission requirements;
   - instead requires the executor to treat plan/context/status as protected read-only paths and to prove in its mutation audit that it did not modify them;
   - may record current plan/context hashes as informational “read at dispatch” evidence only, not as fail-closed candidate admission inputs;
   - keeps immutable packet, design-review, source, sidecar, contract, recovery, candidate 502/501/500, render, mutable-file and receipt hash bindings fail-closed;
   - preserves the original rule that only the main orchestrator may edit canonical plan/context/status.

### P2

None.

## Review of requested design points

- Resolves prior P1 defect classes: conceptually yes. The packet directly targets stale QA recovery/source/ledger/inventory binding and missing verifier/test enforcement.
- Inventory rule: accepted. `output_inventory` as every regular candidate file except root `RECONSTRUCTED_EN.qa.json` is non-circular, complete, and reproducible. The 501-file baseline digest independently matches live state.
- `COMMANDS.json` update ordering: accepted. Deriving command evidence first, then deriving the 501-row inventory including `COMMANDS.json`, then writing QA avoids QA self-reference and permits deterministic validation.
- Local-source-only policy: accepted. The packet requires exact local source path, validates the sidecar, forbids opening the external locator, and rejects byte-identical copies elsewhere.
- Mutable allowlist: accepted in shape. Limiting writes to `scenario_source_reconstruction.py`, `test_scenario_source_reconstruction.py`, candidate `COMMANDS.json`, candidate `RECONSTRUCTED_EN.qa.json`, and the executor receipt is the correct minimal surface. Protecting `reconstruct_scenario_source.py` is coherent because the CLI already exposes the needed actions/flags.
- Baseline/post manifests: accepted for candidate/source/recovery/render artifacts. The live recomputation matches the packet's 502/501/500 and visual manifests. The only rejected part is fail-closed exact binding to mutable plan/context hashes.
- Negative mutation matrix: accepted and appropriately broad. It covers the observed live P1 symptoms and direct analogues.
- Verifier fail-closed semantics: accepted. The required `verify()` checks are sufficient to prevent the current stale QA file from passing after remediation.
- State/semantic blockers: accepted. The packet preserves `candidate_needs_review` and keeps semantic, reading-order, visual, asset ownership and placement uncertainty open.
- Visual QA carry-forward: accepted. Carry-forward is safe only if the prior QA correction hash, render manifests, protected candidate manifest, mutation audit and strict verify all prove reviewed pixels did not change.
- No rebuild/MinerU/OCR/Git/promotion: accepted, except that the packet asks the executor to capture exact Git status as audit evidence. I treat that as read-only audit intent, not Git mutation; if the orchestrator wants zero Git command invocations for executor too, it should replace that with read-only `.git` metadata/status-equivalent file inspection.

## Recommendation and safe next gate

Recommendation: REJECT.

Implementation authorization: not authorized. The executor must not run the packet as written because its plan/context hash bindings are already stale and would fail before any candidate-safe write.

Safe next gate:

1. Orchestrator should request a very narrow amendment that removes exact plan/context hashes from executor fail-closed admission while preserving plan/context/status as protected read-only paths in the mutation audit.
2. After a fresh independent critic accepts that amendment with no P0/P1, the bounded executor may perform only the intended metadata-integrity remediation:
   - update `scenario_source_reconstruction.py` and `test_scenario_source_reconstruction.py`;
   - update candidate `evidence/COMMANDS.json` and `RECONSTRUCTED_EN.qa.json`;
   - write `luna_executor_viral_step6a_qa_metadata_integrity_remediation_20260831.md`;
   - use only local source `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`;
   - preserve candidate state `candidate_needs_review`;
   - perform no build, MinerU/OCR/GPU/model/network/history/translation, source/sidecar/candidate protected-path mutation, promotion, acceptance, publication or Git mutation.
3. Separate bounded QA and a fresh independent implementation/process review remain required before Step 6A can advance to semantic review. This review does not authorize `MASTER_EN`, release, or publication.

Blockers: one P1 finding above.
