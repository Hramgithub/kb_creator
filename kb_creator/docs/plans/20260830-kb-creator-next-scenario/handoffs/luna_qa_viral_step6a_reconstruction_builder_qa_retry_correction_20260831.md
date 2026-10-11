# Viral Step 6A reconstruction-builder QA retry correction receipt

- **Disposition: PASS — bounded remediation QA passed; candidate remains `candidate_needs_review`.**
- Role: bounded QA `gpt-5.6-luna` / low; token use unavailable.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Candidate was not accepted, promoted, committed, or published.

## Receipt binding and correction

The predecessor receipt `luna_qa_viral_step6a_reconstruction_builder_qa_retry_20260831.md`
has SHA-256 `0C2F6A017E15C5FCD91BC429606BAD9DA0E9B2ED4FF3D0DAEECFC3D929096420`.
It is immutable and is not edited here. Its final disposition was internally
contradictory: it said blocked for missing source while also recording two
successful exact external-source verifies. This correction receipt supersedes
that disposition only for the corrected source-flow QA record.

Runtime source used exclusively in this correction:
`kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`, 20,718,150 bytes,
SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
The retained local admission sidecar
`kb_creator/working/viral/source/SOURCE_ADMISSION.json` has SHA-256
`3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9` and records
the external path as provenance only with `runtime_dependency=false`. The
external Yandex path was not opened or used for evidence in this turn.

## Rechecks

- Focused hermetic tests: `126 passed in 0.18s`.
- Corrected local-source `verify` was run twice with separate arguments:
  `--contract kb_creator/contracts/viral.json`, local admitted `--source`,
  `--recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate`,
  and current candidate `--run-root
  kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`.
  Both returned `verified_candidate_needs_review`, `deterministic=true`,
  contract SHA `C2EF2DD143E304F59C8973E8DB82CF83B094BC35DDA37BB2299686E1FE6DA194`,
  source SHA as above, and counts pages/renders `124/124`, sheets `31`, assets
  `204`, referenced/unreferenced `112/92`, anchors `124`, handouts/maps/pregens
  `39/7/13`, back cover `1`.
- Candidate post-manifest assertion: exactly `502` ordinal regular files,
  SHA-256 `52E44F725AB121EC61A255B747EA467B4371481F391EB5E79B51132E67258066`.
- Contact sheets: 31 unique sheets, exact 2x2 mappings `1-4` through
  `121-124`; all sheets viewed, with no visible rotation, cropping, blank or
  corrupt render, or legibility defect. Pages 1–5 remain `unknown` review rows;
  semantic/reading-order/placement uncertainty remains open as required.

## Original-resolution visual coverage

All 67 required pages were covered: `1-6, 19, 32, 45, 58, 68-124`.

- 64 direct original render views were completed.
- Pages `77`, `96`, and `105` were normalized to deterministic RGB PNG copies
  in the authorized disposable probe
  `D:\NRI\_viral_step6a_reconstruction_builder_qa_retry_probe_20260831` and
  each was viewed successfully:
  - page 77: map with notes, legible and uncropped;
  - page 96: window/plague-monk handout, legible and uncropped;
  - page 105: island map, legible and uncropped.
- The three source PNGs were independently PIL-valid and the normalized copies
  were bound to their source page numbers and source render hashes. No visual
  defect was found.
- Probe cleanup: exact probe path deleted; final check `probe_absent=true`.

## Schema and safety disposition

The verified schema is truthful: 204 asset rows comprise 112 referenced and 92
retained unreferenced rows; asset hashes/paths/reference locations are present,
ownership remains null/open where unresolved; 124 unique resolved page anchors
have prev/next links; closures are 39 handouts, 7 maps, 13 pregens, and page
124; blocker ledger/open states and source/recovery hashes remain explicit; no
fabricated final labels, TOC targets, names, or placements were accepted; all
112 Markdown references resolved under verify.

No PDF/cache/runtime/.pyc/reparse-point or forbidden side effect was introduced.
No implementation, candidate, test, source, contract, recovery, predecessor,
plan/context, production/publication, external-source, MinerU/OCR/GPU/model/
network/history/translation, cleanup-root, staging, commit, push, acceptance,
or promotion operation was performed. Existing unrelated worktree dirt remains
unchanged. This correction receipt is the only durable write of this turn.

Next gate: fresh independent `gpt-5.5` critic review. This QA pass does not
authorize candidate acceptance or promotion.
