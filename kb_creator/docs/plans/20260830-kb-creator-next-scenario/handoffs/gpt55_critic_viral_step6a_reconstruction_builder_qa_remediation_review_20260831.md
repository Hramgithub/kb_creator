# Independent critic review: Viral Step 6A reconstruction-builder QA remediation after corrected local-source QA

## Receipt metadata

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6-source-reconstruction-step6a-reconstruction-builder-qa-remediation`
- Review kind: implementation/process, release-style boundary review only
- Role/model/effort requested: fresh independent critic, `gpt-5.5`, medium
- Actual platform model/effort: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol`, medium
- Assignment state: `nri-independent-critic`
- Scoped override: none
- Independence declaration: I did not implement, materially design, remediate, execute, or QA the candidate under review.
- Timestamp: 2026-08-31T22:24:53+03:00
- Elapsed time: unavailable until runtime goal completion metadata
- Token use: unavailable until runtime goal completion metadata
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`, verified by read-only Git metadata file inspection, not by invoking Git

## Verdict

REJECT.

The corrected local-source QA establishes useful evidence, but the live candidate and verifier still have P1 evidence-integrity defects. Step 6A must not be accepted and must not advance to the next semantic review boundary until these are corrected and independently re-reviewed.

This is not a `MASTER_EN`, product-release, accepted-output, or publication review.

## Candidate and receipt identities checked

Local runtime source:

- Runtime source path used for review: `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`
- Bytes: `20,718,150`
- SHA-256: `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`
- Admission sidecar: `kb_creator/working/viral/source/SOURCE_ADMISSION.json`
- Sidecar SHA-256: `3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9`
- External Yandex locator: not accessed; treated only as provenance recorded in the sidecar.

Bound packet/receipt hashes:

- Original remediation packet `terra_engineering_viral_step6a_reconstruction_builder_qa_remediation_packet_20260831.md`: `D7A283D3D6C49701C265707507015870C90C3B1D8B79117BD9F59D2D07622D27`
- Baseline amendment `terra_engineering_viral_step6a_reconstruction_builder_qa_remediation_baseline_amendment_20260831.md`: `C0D8CB1F4B3B9C49A1FC5D013525F37A6459A9EF37DF7F27C3EBB29DC940341C`
- Amendment critic accept `gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_baseline_amendment_review_20260831.md`: `76075D8BBE6880AD659D9EBBA6DAEE96F84909DE8FF508C02D71C2FFC992781F`
- Remediation executor receipt `luna_executor_viral_step6a_reconstruction_builder_qa_remediation_20260831.md`: `978BFD522C4D50668B13D5BB83346D7B86A2F3D663EAE634641495DEFC6E2783`
- Invalid predecessor QA receipt `luna_qa_viral_step6a_reconstruction_builder_qa_retry_20260831.md`: `0C2F6A017E15C5FCD91BC429606BAD9DA0E9B2ED4FF3D0DAEECFC3D929096420`; treated as immutable contradictory history, not acceptance evidence
- Corrected QA receipt `luna_qa_viral_step6a_reconstruction_builder_qa_retry_correction_20260831.md`: `194BF7EE471FF7E7DF859ED7958F7B3978F0F6C54536136C26CC6C6D1A7765DD`

Live implementation/test hashes:

- `kb_creator/scripts/scenario_source_reconstruction.py`: `916D1A117C8FD09691502E1D2EB1DD1BF8FD9112229FE8616E770A17EBE2A446`
- `kb_creator/scripts/reconstruct_scenario_source.py`: `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA`
- `kb_creator/tests/test_scenario_source_reconstruction.py`: `962BEC2E1A8A407FD11D8A088FBCDD18E40175F0B7C6A7B9A1DAE77E1303D63E`

Live candidate root:

- `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`
- Regular files: `502`
- Ordinal canonical manifest SHA-256: `52E44F725AB121EC61A255B747EA467B4371481F391EB5E79B51132E67258066`
- Pages: `124`
- Source renders: `124`
- Contact sheets: `31`
- PDFs/cache/runtime/`.pyc`/reparse-like payload classes checked: none observed
- Candidate state in `RECONSTRUCTED_EN.qa.json`: `candidate_needs_review`

## Files checked

Read fully or inspected read-only:

- `D:\NRI\AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- Accepted builder/remediation packet and critic chain named above
- Remediation executor receipt named above
- Invalid predecessor QA and corrected QA receipt named above
- Local source PDF and `SOURCE_ADMISSION.json`
- Live implementation/test files named above
- Live candidate JSON/evidence/manifests under the candidate root

Changed files:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_review_20260831.md`

Forbidden actions not performed: no external source access, no MinerU, no OCR, no build/remediate, no GPU/model, no network, no historical translation/config access, no candidate/code/test/contract/plan/context/source/sidecar mutation, no Git command, no Git index/ref/commit/push mutation.

## Findings

### P0

None.

### P1

1. `RECONSTRUCTED_EN.qa.json` is stale and internally inconsistent after remediation.

   Evidence:

   - Live `SOURCE_IDENTITY.json` correctly records the admitted recovery manifest/evidence hashes: `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169` and `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC`.
   - Live `RECONSTRUCTED_EN.qa.json` still records stale `recovery_manifest_sha256` as `C32CCA2A85F8123A2BE9E015FB39642943E31FCD723FA466FA436FA436F454B344C3A` and has no `recovery_evidence_sha256` value.
   - Live `evidence/BLOCKER_LEDGER.json` has `open_count: 4` and four open rows, but `RECONSTRUCTED_EN.qa.json` reports `open_blocker_count: 3`.
   - Live `RECONSTRUCTED_EN.qa.json` has `output_inventory` length `470`, i.e. the pre-remediation inventory shape. It still records stale hashes for remediated files, for example:
     - `SOURCE_IDENTITY.json` inventory row SHA `1F6E4157CBD01C1A435DE360CD0577BBBD005DB895FC3047723B0C28A058B900`, while the live file SHA is `276430E8AFC7C8310421D661F9753F0DB4AFBD1091D9B0B9C34084BB2BE438AC`.
     - `evidence/ASSET_PROVENANCE.json` inventory row SHA `506E9F62BDF2EA7ED85FA242F5067807A238ADD951146B93737F92ED35D2D5F8`, while the live file SHA is `BEA4C9B69C28B91DCDF331A628E2A7AE6A25E6E223FA336CC863BF5DE8456881`.
     - No `renders/contact_sheets/sheet-001.png` row appears in that inventory, although the live sheet exists with SHA `D5658A02ADFDB1B0BB97D0E80BDDACADA33947FA2B017E6F8C7A763A5BBB63A9`.

   Why this blocks: this stage is evidence-bound. A candidate may remain `candidate_needs_review`, but its QA manifest cannot carry stale source/recovery bindings, stale inventory rows, or undercounted open blockers. Advancing to semantic review on this evidence would force the next reviewer to reason from a self-contradictory QA record.

   Required remediation: under a new narrow remediation packet or orchestrator-authorized bounded executor task, regenerate `RECONSTRUCTED_EN.qa.json` so that it:

   - records admitted recovery manifest/evidence hashes `41F00E...` and `F1F9F...`;
   - reports `open_blocker_count` equal to the live blocker ledger's `open_count` and row count;
   - either removes `output_inventory` if replaced by the external ordinal manifest receipt, or clearly defines and regenerates it against the post-remediation candidate using a self-consistent rule, such as all regular files except `RECONSTRUCTED_EN.qa.json`;
   - includes contact-sheet and remediated-evidence hashes if the inventory is retained;
   - keeps state `candidate_needs_review` and keeps all semantic/reading-order/placement/ownership uncertainty open.

2. Live verifier and focused tests do not validate the evidence integrity required by the accepted packets.

   Evidence:

   - `scenario_source_reconstruction.py:180` updates selected `RECONSTRUCTED_EN.qa.json` count/gate fields but does not update the stale recovery hash, missing recovery evidence hash, stale `output_inventory`, or `open_blocker_count`.
   - `scenario_source_reconstruction.py:227-241` verifies topology, counts, assets/navigation/sheets, candidate state, and baseline change, but does not validate `RECONSTRUCTED_EN.qa.json` recovery hashes, blocker-count consistency, output inventory consistency, contact-sheet inventory rows, or live remediated evidence hashes.
   - `test_scenario_source_reconstruction.py:37-44` tests only the amended baseline constant and a simple ordinal sort example. The remediation packet required focused hermetic tests for exact allowed delta, 31-sheet mapping/missing/duplicate refusal, 204/112/92 conservation and references, 124 navigation anchors, source/recovery bindings, stale flag rejection, and verify refusal for wrong mutable schema/count/hash. The current live test file does not cover the stale QA fields that are present in the candidate.

   Why this blocks: the corrected QA receipt reports `126 passed`, but 119 of those are the Step 5 contract tests and the seven Step 6A tests are largely static/string-level checks. The passing test count therefore does not prove the remediation evidence is internally consistent. Since `verify` can pass while the live candidate has stale QA metadata, Step 6A implementation/process acceptance is not safe.

   Required remediation: extend `verify` and focused hermetic tests so they fail when:

   - `RECONSTRUCTED_EN.qa.json` recovery hashes do not match admitted recovery manifest/evidence;
   - `open_blocker_count` differs from `BLOCKER_LEDGER.json`;
   - retained `output_inventory` rows do not match the chosen post-remediation inventory rule;
   - contact-sheet rows/hashes are missing from retained inventory;
   - asset/navigation/page/count fields are internally inconsistent;
   - runtime command evidence uses the external locator instead of the admitted local source or omits required no-runtime/no-network/no-build flags.

### P2

None.

## Positive evidence

The following reviewed facts are sound and should be preserved in the next remediation:

- Source-flow correction is correct: `SOURCE_ADMISSION.json` records the external locator as one-time provenance with `runtime_dependency=false`; the local retained PDF is byte-identical to the admitted source and is the only runtime source for future commands.
- The live candidate remains `candidate_needs_review`.
- Live root cardinalities match the correction QA: 502 regular files, 124 page files, 124 source renders, 31 contact sheets, 204 asset rows, 124 navigation anchors, 39 handouts, 7 maps, 13 pregens, 1 back cover.
- `ASSET_PROVENANCE.json` truthfully keeps 204 rows as 112 referenced plus 92 unreferenced engine-evidence rows; unresolved ownership remains open/null rather than fabricated.
- `NAVIGATION_INVENTORY.json` has 124 unique page anchors with correct 0-based engine index to 1-based source page mapping, prev/next links, and fixed role partitions.
- `BLOCKER_LEDGER.json` keeps semantic/reading-order/placement/ownership uncertainty open.
- Candidate JSON and command evidence inspected did not contain the external Yandex path; `SOURCE_ADMISSION.json` is the only inspected file that records it, and there it is provenance-only.
- The invalid predecessor QA receipt is correctly treated as immutable contradictory history, not acceptance evidence; the correction QA receipt supersedes only that disposition.

## Review conclusions

- Correctness: not accepted due to stale QA metadata and insufficient verifier/test coverage.
- Source-flow correction: accepted in principle; local retained source and sidecar are valid and should remain the only runtime source evidence.
- Provenance/runtime separation: mostly sound, but blocked by stale `RECONSTRUCTED_EN.qa.json` recovery/inventory provenance.
- Packet/receipt binding: receipt hashes match the supplied chain; invalid QA predecessor is correctly excluded from acceptance.
- Baseline/delta: live post-manifest matches `52E44F725AB121EC61A255B747EA467B4371481F391EB5E79B51132E67258066`, but candidate-internal inventory evidence does not match post-state.
- Code/tests/schema determinism: not accepted; verifier and tests do not catch observed stale evidence.
- Candidate immutability: preserved during this review; no mutation performed.
- Visual QA sufficiency: correction QA's 67/67 visual coverage is acceptable as bounded visual evidence for this stage, but it cannot override the metadata/verifier P1s.
- Blocker ledger truthfulness: ledger itself is truthful; QA summary undercounts it.
- Fabricated semantic closure: none found. Open ownership/placement/reading-order/mode uncertainty remains open.

## Recommendation and next authorized gate

Recommendation: REJECT.

Implementation/process authorization: not authorized for Step 6A acceptance or advancement to the next semantic review boundary while P1 findings remain.

Next authorized gate:

1. Orchestrator should prepare a narrow remediation packet or bounded executor task limited to fixing candidate QA metadata consistency and verifier/test coverage.
2. That remediation may touch only the already accepted minimal surfaces needed for the P1s: `scenario_source_reconstruction.py`, `reconstruct_scenario_source.py` if CLI proof changes are needed, `test_scenario_source_reconstruction.py`, `RECONSTRUCTED_EN.qa.json`, and any directly affected evidence/command JSON if the chosen inventory rule requires it.
3. It must use only the local admitted source `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`, preserve `SOURCE_ADMISSION.json`, keep the external locator provenance-only, and keep candidate state `candidate_needs_review`.
4. It must not rebuild, rerun MinerU/OCR/GPU/model/network, access historical translations/config, promote to `MASTER_EN`, accept/publish, mutate plan/context/status/source/sidecar outside explicit scope, or perform Git operations.
5. After remediation, rerun bounded QA and a fresh independent implementation/process review.

Acceptance after that review remains limited to Step 6A reconstruction-builder/remediation boundary only, not `MASTER_EN` promotion or final product release.

Blockers: two P1 findings above.
