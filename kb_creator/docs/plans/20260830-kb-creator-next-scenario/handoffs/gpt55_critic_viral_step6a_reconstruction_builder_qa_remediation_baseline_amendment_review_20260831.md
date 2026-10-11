# Independent critic review: Viral Step 6A QA-remediation baseline amendment

## Receipt metadata

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6-source-reconstruction-step6a-reconstruction-builder-qa-remediation-baseline-amendment`
- Review kind: process/architecture
- Role/model/effort requested: fresh independent critic, `gpt-5.5`, medium
- Actual platform model/effort: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol`, medium
- Assignment state: `nri-independent-critic`
- Scoped override: none
- Independence declaration: I did not implement, materially design, or remediate the baseline amendment, the original QA-remediation packet, or the candidate under review.
- Timestamp: 2026-08-31T21:18:38+03:00
- Elapsed time: unavailable until runtime goal completion metadata; active review was bounded to the assigned amendment
- Token use: unavailable until runtime goal completion metadata
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`

## Candidate identity

Reviewed amendment:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_builder_qa_remediation_baseline_amendment_20260831.md`
- Expected SHA-256: `C0D8CB1F4B3B9C49A1FC5D013525F37A6459A9EF37DF7F27C3EBB29DC940341C`
- Observed SHA-256: `C0D8CB1F4B3B9C49A1FC5D013525F37A6459A9EF37DF7F27C3EBB29DC940341C`
- Hash result: pass

Bound predecessor identities verified:

- Original QA-remediation packet `terra_engineering_viral_step6a_reconstruction_builder_qa_remediation_packet_20260831.md`: `D7A283D3D6C49701C265707507015870C90C3B1D8B79117BD9F59D2D07622D27`
- Prior independent reject receipt `gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_packet_review_20260831.md`: `7BBC78D57C1D91D3438B025B44D5C437B73A1F0F5D3339C05C1571B82F3D5BC7`

## Scope and files checked

Read fully or inspected read-only for this review:

- `D:\NRI\AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_builder_qa_remediation_packet_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_packet_review_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_builder_qa_remediation_baseline_amendment_20260831.md`
- Candidate root, read-only:
  - `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`

Changed files:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_baseline_amendment_review_20260831.md`

No candidate, implementation, test, plan, context, status, source, recovery root, accepted/production/publication output, Git index, commit, or push mutation was performed. I did not run remediate, build, MinerU, OCR, GPU/model, network, or historical translation/config access.

## Baseline recomputation evidence

The amendment defines the canonical baseline algorithm as:

1. Recursively enumerate regular files under the exact candidate root.
2. Render each relative path with POSIX `/` separators.
3. Build complete records as `relative-posix-path<TAB>byte-count<TAB>uppercase-SHA256(file)`.
4. Sort complete record strings using `.NET StringComparer.Ordinal` / Unicode code-point ordinal ordering.
5. Join records with LF, append one final LF, encode as UTF-8 without BOM.
6. SHA-256 the resulting byte stream and render uppercase hex.

Live candidate recomputation:

- Candidate root: `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`
- Regular file count: `471`
- PowerShell/.NET ordinal digest: `BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809`
- Python corroboration over the same complete-record strings: `BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809`
- First ordinal record: `RECONSTRUCTED_EN.md	18259	259B25D61D9BBFBB6314411DD73B257B56ECDFD8480B6E3EAD3DBCCA35DB5601`
- Last ordinal record: `renders/source/page-124.png	2980641	538ABBDC680CBAB6AC9A7F7A2FD1E5AE70F8BC405C290EA54E34A9DFC3875DE6`
- Result: pass. The amendment's required digest matches the live candidate under the amended algorithm.

## Assessment

The amendment directly resolves the prior P1 baseline-binding defect. It replaces only the erroneous `6E0872BA47E74356E590D7CFABE192ED92DD832D1B11CAA1BDBBE120AFFC4E07` digest with the reproducible live candidate digest `BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809`.

The amendment is appropriately narrow. It explicitly supersedes only the wrong candidate-baseline digest in the original packet's baseline-admission table and ready-to-paste executor prompt. It preserves all other original packet controls: exact in-place write allowlist, immutable paths, no new root, no rebuild, no MinerU/OCR/GPU/model/network/history, no Git mutation, successor executor receipt, downstream QA retry, final independent review, and `candidate_needs_review` only.

The amended algorithm is more precise than the original packet because it fixes culture-sensitive ordering ambiguity by requiring complete-record ordinal sorting, UTF-8 without BOM, uppercase per-file hashes, LF serialization, and a final LF. The duplicate PowerShell/Python recomputation requirement is a reasonable fail-closed reproducibility guard for this small 471-file baseline.

## Findings

### P0

None.

### P1

None.

### P2

None.

## Required review points

- Live 471-file candidate manifest recomputation: pass. Observed digest equals expected `BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809`.
- Exact amendment algorithm: acceptable and deterministic. It avoids locale/culture collation drift and binds a final-LF UTF-8-no-BOM byte stream.
- Supersession scope: acceptable. The amendment supersedes only the wrong `6E0872...` digest and keeps the original remediation packet controls unchanged.
- Original packet controls: preserved. No broader mutation, candidate rebuild, root recreation, source/contract/recovery modification, runtime launch, historical translation/config access, promotion, or release/acceptance is introduced.
- Execution authorization: acceptable after orchestrator integrates this review, because no P0/P1 remains.

## Recommendation and authorization decision

Recommendation: accept.

Implementation authorization: authorized after orchestrator resolution of this receipt. The accepted execution boundary is the original QA-remediation packet plus this baseline amendment.

Exact authorized boundary:

- Executor may perform only the bounded in-place QA remediation after first recomputing the amended baseline digest twice and obtaining `BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809` both times.
- Executor may write only the original packet's allowlisted paths: three generic source/test paths, mutable candidate metadata/evidence JSONs, exactly `renders/contact_sheets/sheet-001.png` through `sheet-031.png`, and the successor executor receipt.
- Executor must preserve immutable candidate pages, source renders, copied engine payload, `RECONSTRUCTED_EN.md`, `SCENARIO_CONTRACT.json`, source PDF, recovery roots, plan/context/status, accepted/production/publication outputs, and Git state.
- Executor must not run build, MinerU, OCR, GPU/model, network, historical translations/config, cleanup, stage, commit, or push.
- Candidate state must remain `candidate_needs_review`; any promotion, baseline mismatch, invented semantic, forbidden side effect, unexpected write, missing sheet, count/hash/schema failure, or reproducibility mismatch is a stop.

Residual risks:

- The amendment fixes only baseline admission. It does not prove the future remediation implementation, generated contact sheets, asset/navigation rows, QA retry, or final Step 6 acceptance.
- Visual/layout fidelity and semantic completeness remain review-dependent until the required QA retry and subsequent independent implementation/process review pass.

Blockers: none.

Next action: orchestrator may assign the bounded executor QA-remediation task under the original packet plus this accepted baseline amendment.
