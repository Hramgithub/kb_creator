# Independent critic review: Viral Step 6A reconstruction-builder QA remediation packet

## Receipt metadata

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6-source-reconstruction-step6a-reconstruction-builder-qa-remediation`
- Review kind: process/architecture
- Role/model/effort requested: fresh independent critic, `gpt-5.5`, medium
- Actual platform model/effort: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol`, medium
- Assignment state: `nri-independent-critic`
- Scoped override: none
- Independence declaration: I did not implement, materially design, or remediate the QA remediation packet or the candidate under review.
- Timestamp: 2026-08-31T21:10:58+03:00
- Elapsed time: unavailable until runtime goal completion metadata; active review was bounded to the assigned packet
- Token use: unavailable until runtime goal completion metadata
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`

## Candidate identity

Reviewed packet:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_builder_qa_remediation_packet_20260831.md`
- Expected SHA-256: `D7A283D3D6C49701C265707507015870C90C3B1D8B79117BD9F59D2D07622D27`
- Observed SHA-256: `D7A283D3D6C49701C265707507015870C90C3B1D8B79117BD9F59D2D07622D27`
- Hash result: pass

Bound predecessor identities verified:

- Accepted builder packet `terra_engineering_viral_step6a_reconstruction_builder_packet_20260831.md`: `F5B5684591586BFE7C22D0F73C67B4B3A849A206495FFEFF8261E3CE2E97138C`
- Accepted builder-packet critic receipt `gpt55_critic_viral_step6a_reconstruction_builder_packet_review_20260831.md`: `1F496F465C0A18A10DFC32FEA0535970603B1449ECC50E2C790E7E36D339E2AB`
- Executor receipt `luna_executor_viral_step6a_reconstruction_builder_20260831.md`: `5E5A059BDD4CA9A431AAAE84079A66CE1BFD037215BE4AA9B505298162D4CFB0`
- Failed QA receipt `luna_qa_viral_step6a_reconstruction_builder_20260831.md`: `4FDE96841683DA0516E80439EC11476BC27BE9366E885673379AC8964550C649`

## Scope and files checked

Read fully or inspected read-only for this review:

- `D:\NRI\AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_builder_packet_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstruction_builder_packet_review_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_reconstruction_builder_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_reconstruction_builder_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_builder_qa_remediation_packet_20260831.md`
- Candidate root, read-only:
  - `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`
- Current implementation seam, read-only:
  - `kb_creator/scripts/scenario_source_reconstruction.py`
  - `kb_creator/scripts/reconstruct_scenario_source.py`
  - `kb_creator/tests/test_scenario_source_reconstruction.py`

Changed files:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_packet_review_20260831.md`

No candidate, implementation, test, plan, context, status, source, recovery root, accepted/production/publication output, Git index, commit, or push mutation was performed. I did not run remediate, build, MinerU, OCR, GPU/model, network, or historical translation/config access.

## Evidence checked

Live candidate baseline observed read-only:

- Candidate root exists: `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`
- File count: `471`
- Total bytes: `383,219,086`
- Pages: `124` files under `pages/page-*.md`
- Source renders: `124` files under `renders/source/page-*.png`
- Contact sheets: `0` files under `renders/contact_sheets/*.png`
- PDFs under candidate: `0`
- Cache/runtime/Python bytecode-like payloads under candidate: none observed in the checked path classes
- `evidence/ASSET_PROVENANCE.json`: exists, `rows` length `0`
- `evidence/NAVIGATION_INVENTORY.json`: exists, `rows` length `0`
- `evidence/PAGE_PROVENANCE.json`: exists, `rows` length `124`
- `evidence/HANDOUT_INVENTORY.json`: exists, `rows` length `39`
- `evidence/BLOCKER_LEDGER.json`: exists, `rows` length `3`
- `RECONSTRUCTED_EN.qa.json`: state `candidate_needs_review`; counts include pages `124`, renders `124`, handouts `39`, engine payload `209`, engine images `204`; `open_blocker_count` `3`
- Existing candidate metadata currently serializes recovery manifest/evidence hashes as `C32CCA2A85F8123A2BE9E015FB39642943E31FCD723FA466FA436F454B344C3A` and `050F8A1AB81B660D3F1CF1809C77DB5AE57B41C9545EF72DA945A7204582FCFE`, which the packet correctly treats as mutable metadata drift to correct back to the admitted `41F00E...` / `F1F9F...` values.

Canonical baseline manifest recomputation:

- The remediation packet states the baseline manifest is SHA-256 over UTF-8 bytes of sorted LF records `relative-posix-path<TAB>byte-count<TAB>SHA256(file)\n`.
- Recomputing that stated format from the live 471-file candidate with uppercase file SHA-256 values gives: `BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809`.
- Lowercase SHA-256 values with LF give: `535ACBDD8890F7D66B153542B194F158FA0C59BCD2210F8C31DD748A4091EE08`.
- Uppercase SHA-256 values with CRLF give: `C04B8188688B231BB1BF4B340425D0FDE3BBCB37E6497E00C42D76C735D7F54D`.
- Lowercase SHA-256 values with CRLF give: `1BB5B9120652E07D12DAFAB987247E5031C0E2A65CECA3C4FE75FAF85A7EF5E1`.
- None match the packet's required candidate baseline `6E0872BA47E74356E590D7CFABE192ED92DD832D1B11CAA1BDBBE120AFFC4E07`.

## Assessment

The remediation packet is conceptually scoped to the actual QA failures: missing contact-sheet coverage, empty asset/navigation provenance, and stale executor command documentation. Its in-place remediation boundary is otherwise appropriate: it keeps the candidate in `candidate_needs_review`, preserves immutable pages/source renders/engine payload/source/contract/recovery roots, corrects mutable metadata drift rather than treating it as authority, and requires a successor executor receipt plus a separate QA retry before any Step 6 acceptance.

The packet's contact-sheet requirement is feasible and deterministic in principle: 31 fixed 2x2 sheets cover 124 existing source renders exactly. The requested downstream QA burden is large but bounded and correctly separates contact-sheet coverage from detailed original-resolution review of risk pages.

The asset/navigation closure requirements are also truthful in principle. A 204-row asset inventory with 112 referenced and 92 retained-unreferenced engine rows avoids fabricating placement ownership. A navigation inventory with at least 124 page anchors and review-only handout/map/pregen/back-cover coverage is consistent with `candidate_needs_review`.

However, the packet is not executable as a safe in-place remediation because its baseline manifest binding does not match the live candidate under the packet's own stated canonical manifest definition. Since baseline admission is the gate that prevents accidental remediation of the wrong root or wrong state, this is a P1 blocker.

## Findings

### P0

None.

### P1

1. Candidate baseline manifest binding is invalid.

   Evidence: the packet requires the exact existing candidate root to have canonical manifest SHA-256 `6E0872BA47E74356E590D7CFABE192ED92DD832D1B11CAA1BDBBE120AFFC4E07`. I recomputed the stated canonical format from the live 471-file candidate root. The observed uppercase-LF digest is `BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809`; lowercase-LF, uppercase-CRLF, and lowercase-CRLF variants also do not match `6E0872...`. The failed QA receipt establishes the same root cardinality and failure state, and the live root still has 471 files, 0 contact sheets, 0 asset rows, and 0 navigation rows.

   Why this blocks: the packet's own admission model says the executor must stop before any write if baseline binding fails. Accepting this packet would either force a correct executor to block immediately or tempt an executor to bypass the baseline guard. That weakens the in-place mutation control that is the core safety mechanism for this remediation.

   Required remediation: issue a corrected immutable remediation packet or amendment that either (a) replaces `6E0872BA47E74356E590D7CFABE192ED92DD832D1B11CAA1BDBBE120AFFC4E07` with the live candidate baseline digest `BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809` under the stated uppercase-LF manifest formula, or (b) defines a different exact canonical manifest formula and provides a reproduced digest that matches the live candidate. The corrected packet must keep the same fail-closed rule: any baseline mismatch stops before remediation.

### P2

None.

## Required review points

- Baseline manifest binding: not accepted; P1 above.
- Exact in-place write allowlist: acceptable in shape. It is narrow enough to cover code/test changes, mutable candidate metadata/evidence, 31 contact sheets, and the successor executor receipt while preserving source, contract, pages, master Markdown, source renders, copied engine payload, recovery roots, accepted/production/publication outputs, plan/context/status, and Git.
- Feasibility and determinism of 31 2x2 sheets: acceptable. The candidate already has 124 source renders and no contact sheets; 31 four-page sheets are deterministic if generated only from existing render files and fixed encoder/layout settings.
- Full visual QA: acceptable as a downstream QA requirement. It is bounded by all 31 sheets plus original-resolution review sets and correctly keeps unresolved fidelity/reading-order/label/placement/mode issues as `needs_review`.
- Truthful 204/112/92 asset rows: acceptable. The packet explicitly forbids fabricating PDF xrefs, final semantic roles, or ownership.
- 124 navigation anchors and 39/7/13/page124/pages1-5 closure: acceptable. The packet preserves pages 1-5 as unknown-mode review anchors and does not claim final navigation semantics.
- Immutable paths: acceptable, subject to fixing the baseline hash. The packet correctly forbids full rebuild, root deletion/recreation, MinerU/OCR/model/network use, and source/origin PDF copying.
- Corrected successor receipt flags: acceptable. Governance is correctly handled by superseding the stale executor command text in a new receipt rather than editing the immutable predecessor.
- Tests/stops/audits: acceptable in concept. The proposed hermetic test surface directly targets baseline admission, allowed delta, contact-sheet coverage, asset conservation, navigation closure, stale CLI flag rejection, and verify refusal modes.
- `candidate_needs_review` boundary: acceptable and preserved.
- Downstream QA/review order: acceptable. No Step 6 acceptance or `MASTER_EN` dispatch precedes executor remediation, QA retry, and a fresh independent implementation/process review.

## Recommendation and authorization decision

Recommendation: reject.

Implementation authorization: not authorized. The executor must not run this remediation packet as written because the declared baseline manifest does not bind the live candidate root.

Corrected authorization boundary after remediation:

- A successor engineering packet or amendment may preserve this packet's scope and controls but must correct the baseline manifest identity.
- After a fresh independent critic accepts the corrected packet with no P0/P1, the executor may perform only the bounded in-place remediation: closed `remediate`, 31 contact sheets, non-empty truthful asset/navigation provenance, corrected mutable candidate metadata/evidence, focused tests, preflight/remediate/verify, successor receipt, and no promotion beyond `candidate_needs_review`.

Residual risks after baseline correction:

- Visual/layout fidelity remains review-dependent until QA actually reviews all sheets and original-risk renders.
- The 204 asset rows and 124 navigation rows can be truthful review scaffolding, but they still must not be mistaken for final semantic placement or publication readiness.
- Any mutation to the candidate root after a corrected baseline packet invalidates that packet's baseline and requires recomputation/review.

Blockers: one P1 baseline-binding defect.

Next action: orchestrator should request a corrected remediation packet/amendment with a reproducible candidate baseline manifest hash, then resend for fresh independent critic review before executor remediation.
