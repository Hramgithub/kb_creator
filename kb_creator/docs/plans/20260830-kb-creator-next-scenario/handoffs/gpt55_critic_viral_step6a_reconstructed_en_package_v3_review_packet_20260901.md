# Independent critic packet — Viral Step 6A reconstructed package v3

## Assignment

- Goal: `20260830-kb-creator-next-scenario`.
- Review kind: independent reconstruction candidate review, not release.
- Required role: GPT-5.5 independent critic, reasoning `high`, accelerated
  service when available.
- The critic did not implement or materially design v3, the materializer or the
  finalizer.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.

Review the frozen v3 reconstruction package and decide whether Step 6 source
reconstruction may be accepted and handed to the later explicit-user MASTER_EN
reading boundary. Do not implement, repair, mutate, promote or publish anything.

## Frozen candidate boundary

Package:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v3`

- 377 files / 41068701 bytes;
- Python/codepoint ordinal trailing-LF inventory SHA-256
  `46E61F5DB9853E795C636147C63230936221F056DE1A9C25B19A4C8DEAEA215E`;
- inherited candidate files 373/373 byte-identical;
- only additions: selected overlay plus three reconstruction provenance/QA
  files.

Candidate:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v3`

- 373 files / 13142501 bytes;
- portable inventory SHA-256
  `B0D74C6560648454DD3B12E02446969A11851BD722B41F0222FFA9DE32121EA1`;
- `RECONSTRUCTED_EN.md` SHA-256
  `5D28F097708CB9D58A5A0D4C72CC93E9985FC7CDB00C22EFDB0A22C9931B79ED`.

Selected overlay:

- 27696569 bytes, 124 Letter pages, rotation 0;
- SHA-256
  `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB`.

Any identity mismatch or mutation invalidates the assignment and must be
reported rather than repaired.

## Required evidence

- `kb_creator/contracts/viral.json` and retained source PDF;
- package root artifacts, pages, decisions and assets;
- frozen raw comparison and selected-view visual bundle as needed;
- predecessor v2 rejection receipt SHA-256
  `59CA9BA789CC94710DFCE16C514B77DDC1D67FDA38E4B9ED3DE6017626D798F1`;
- v3 content receipt SHA-256
  `179F289C1177F70B4049FF96306611087A6BE20498D9C35755B0A92B31E81E67`;
- finalizer production-shape receipt SHA-256
  `5FD7C039BFB9B7BE6C903B98BC4FD7E57584CD68C122129B90E3C930BC3A44AE`;
- Luna execution receipt SHA-256
  `343A4B16236E63C2EBF40EED80CF02CD393C2D77DA13DDE273C98A155E48CD99`;
- Luna render-only visual receipt SHA-256
  `BEE706F229F43C7791856B417CCA32252C7D05C39D0BF0132C2B323C5C3CE2B0`;
- orchestrator v3 audit SHA-256
  `27972F88B660374908BC2862F078E4C3492F4BC7149B6284961BB4BD838673F0`;
- materializer SHA-256 `D632FD22...F331076` and finalizer SHA-256
  `E943D82F...F39C367` only as implementation identity; no execution is requested.

## Required independent checks

Recompute enough current-state evidence to decide each gate rather than merely
trusting green labels:

1. `source_identity`: retained source hash/bytes/pages/geometry and embedded
   package provenance agree with contract.
2. `page_coverage`: 124 pages, decisions, source markers and page domains have no
   gap/duplicate.
3. `role_partition`: every page has exactly one contract role from contract
   ranges while preserving its packet-bound fine-grained role. Confirm the v2
   role-partition P1 is closed without mutating frozen merge packets.
4. `text_ocr_provenance`: decision blocks project correctly into package
   provenance and resolve to frozen raw comparison; unresolved lists are empty.
   Confirm the seven page-016 corrections against visual/source evidence and
   look for any regression introduced by them.
5. `required_entity_closure`: exact canonical physical labels are
   `1,2a,2b,3a,3b,4..39`, unique numeric ordinals are exactly 1-39, label pages
   agree with the visual source and page 82 legitimately has none. Confirm the
   v2 handout P1 is closed.
6. `asset_closure`: manifest-declared and actual assets, hashes and all
   reader-facing Markdown links close exactly; decision-only template
   placeholders are not misclassified as reader-facing unresolved content.
7. `no_open_blockers`: no P0/P1/P2 defect is hidden by the summary.
8. `selected_overlay`: 124-page choice domain, selected layout provenance,
   PDF geometry/hash and render evidence close. Evaluate the recorded Poppler
   font warnings in light of 124/124 exact pixel equality.
9. Re-evaluate the v2 P2/P3: portable ordinal identity wording is now exact and
   source identity is embedded in the successor package.

Use P0/P1/P2/P3 severity. Distinguish a genuine reconstruction blocker from a
later MASTER_EN editorial/navigation/readability concern. This review must not
substitute for explicit user reading acceptance of MASTER_EN.

## Allowed write

Exactly one receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstructed_en_package_v3_review_20260901.md`

No other write is allowed. No MinerU, materializer, finalizer, tests,
371/119/490, render build, cleanup, promotion, MASTER_EN, translation, HTML/PDF
publication, production, Git index, commit or push.

## Decision vocabulary

Return exactly one recommendation:

- `accept_reconstruction_candidate`;
- `accept_with_conditions` only for clearly non-blocking downstream conditions;
- `reject_reconstruction_candidate`.

The receipt must include candidate identities, reviewed evidence, gate table,
v2-finding closure table, P0-P3 findings, blockers, recommendation, mutation
boundary, changed-files statement, elapsed time and token use (`unavailable` if
not exposed). Return to the main chat only a compact summary and receipt hash.
