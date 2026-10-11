# Viral Step 6A v4 materialize/finalize execution QA receipt

## Receipt

- Result: **PASS** for the bounded execution and read-only QA assignment.
- Assignment owner: bounded `gpt-5.6-luna` QA execution at `high`.
- Working directory: `D:\NRI\.worktrees\kb-creator-viral`.
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`.
- Assignment state: completed; bounded QA passed.
- Scoped override: `none`.
- Packet: `sol_orchestrator_viral_step6a_v4_materialize_finalize_qa_assignment_20260901.md`; 6,195 bytes; SHA-256 `6835D8003C373B576E4372AB14C4D90330F1A92F61D14D2D36320D7795AE30F4`.
- Timestamp: `2026-09-01T18:32:00.7327346+03:00`.
- Elapsed time: approximately 10 minutes interactively; exact start timestamp was unavailable.
- Token use: unavailable.

This receipt is the sole additional file written by this assignment. No raw
transcript was written. No source, contract, reviewed decisions, frozen
three-view/bundle roots, v1-v3 evidence, code, tests, plan/context/status,
accepted/production roots, p124 publication asset, Git state, MinerU/OCR,
371/119/490 matrix, cleanup, repair, or release action was performed.

## Scope

The only material output roots were the two packet-authorized fresh roots:

- `kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v4`
- `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`

Both were absent before execution. The only additional write is this receipt.

## Exact execution and native results

1. Materializer, run exactly once:

   `python -B kb_creator\scripts\materialize_mineru_ai_merge.py --bundle-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --decisions-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions_v4\pages --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v4`

   - Native exit: `0`.
   - Native stdout: `{"status": "candidate_ready_for_reconstruction_qa", "pages": 124, "assets": 121, "unique_asset_bytes": 121}`.
   - Native stderr: empty.

2. Finalizer, run exactly once after materializer exit 0:

   `python -B kb_creator\scripts\finalize_mineru_reconstruction.py --contract kb_creator\contracts\viral.json --source kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --candidate-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v4 --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_reconstructed_en_package_v4`

   - Native exit: `0`.
   - Native stdout: `{"status": "candidate_ready_for_reconstruction_review", "pages": 124, "overlay_pages": 124}`.
   - Native stderr: empty.

3. Focused fidelity audit, read-only:

   `python -B kb_creator\scripts\audit_mineru_ai_merge_fidelity.py --decisions-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions_v4\pages --merge-packets-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate\merge_packets --reviewed-allowlist kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_fidelity_v4_allowlist.json`

   - Native exit: `0`.
   - Native stdout machine result: schema `kb_creator.ai-merge-fidelity-audit/v1`; 124 page records; `errors: []`; `passed: true`; reviewed p62 `ý -> ÿ` count-7 substitution present and allowlisted.
   - Native stderr: empty.

4. Focused suites, with bytecode and pytest cache disabled:

   `python -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_materialize_mineru_ai_merge.py kb_creator/tests/test_finalize_mineru_reconstruction.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`

   - Native exit: `0`.
   - Native stdout: `62 passed in 9.87s`.
   - Native stderr: empty.

## Deterministic inventories and identities

Portable inventory format is the packet convention: Python/codepoint-ordinal
relative POSIX path sorting, UTF-8 rows
`path<TAB>bytes<TAB>UPPER_SHA256<LF>`.

| Root | Files | Total bytes | Inventory SHA-256 |
|---|---:|---:|---|
| candidate v4 | 373 | 13,152,378 | `EBC5135C61EA0D795D1A879B74B7B6E6127AFDE6406BC520059F997FB316A2E6` |
| reconstructed package v4 | 377 | 41,079,424 | `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83` |

Candidate counts and identities:

- `pages/`: 124 Markdown page files; `decisions/`: 124 JSON decision copies;
  `assets/`: 121 JPEGs, 121 unique SHA-256 values, all filename hashes valid.
- `RECONSTRUCTED_EN.md`: 348,578 bytes; SHA-256
  `243D7258599F038B2C512B675619B1312461EA4CEC97BC2B3E30A5C95C1917BE`.
- `MERGE_PROVENANCE.json`: 232,547 bytes; SHA-256
  `9B0928418E61189B8D15377240730EABBA46D4455D4EA7449338D921168DBCA2`.
- `ASSET_MANIFEST.json`: 50,739 bytes; SHA-256
  `914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9`.
- `OVERLAY_SELECTION.json`: 10,992 bytes; SHA-256
  `B17EF5E777FDDA7E51BADCD3E939B8BFBEC67AFB35FF016FB6AB1B7F7C07353D`.

Package closure:

- All 373 candidate-relative files are present in the package and byte-identical: missing `0`, mismatches `0`.
- Exactly four package-only files exist: `RECONSTRUCTION_PROVENANCE.json`,
  `RECONSTRUCTION_QA.json`, `RECONSTRUCTION_QA.md`, and `SELECTED_OVERLAY.pdf`.
- `RECONSTRUCTION_PROVENANCE.json`: 229,628 bytes; SHA-256
  `0B958506A76A1CB152A0D935A4A78DF0326AE24C5BFEDDC8B59D5434BB9A8460`.
- `RECONSTRUCTION_QA.json`: 643 bytes; SHA-256
  `F88E0474D19982B0634AE66DB7A10F865EA3EDB1DB491AF55E6E3CC5F03EDCC0`.
- `RECONSTRUCTION_QA.md`: 206 bytes; SHA-256
  `162039F13D25D3E25B7D2C60B20845F615425AAE95CF1A8F869025C586195851`.
- `SELECTED_OVERLAY.pdf`: 27,696,569 bytes; SHA-256
  `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB`.

## Required read-only QA

- Candidate and package `RECONSTRUCTED_EN.md` each contain 124 unique ordered
  markers `<!-- source-page-001 -->` through `<!-- source-page-124 -->`.
- Every candidate decision copy is byte-identical to its reviewed v4 input:
  124 inputs, 124 outputs, missing `0`, mismatches `0`.
- Source identity is bound to `Call_of_Cthulhu_Viral.pdf`, 20,718,150 bytes,
  124 pages, SHA-256
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Contract identity is `viral.json`, revision `1`, SHA-256
  `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`.
- Provenance covers 124 ordered page records with nonempty fine-grained and
  contract roles. Handout provenance has 41 physical labels, unique numeric
  ordinals `1..39`, and preserves `2a`, `2b`, `3a`, `3b`.
- `RECONSTRUCTION_QA.json` status is
  `candidate_ready_for_reconstruction_review`; all seven gates pass with
  empty error arrays: `source_identity`, `page_coverage`, `role_partition`,
  `text_ocr_provenance`, `required_entity_closure`, `asset_closure`, and
  `no_open_blockers`.
- No nonempty unresolved JSON lists or placeholder-token files were found in
  either fresh root.
- `SELECTED_OVERLAY.pdf` is 124 pages, all Letter media boxes `(0,0,612,792)`,
  rotation domain `{0}`, and byte-identical to the required v3 overlay hash.
- Receipt-mandated corrected content is present: complete p20 rumor rows;
  p34 STR table; p42/p45 `1O` forms; p49/p50 Hastalÿk titles; p55 throw
  table; p62 corruption token and levels 1–10 ledger; p65/p66 characteristics
  and statblocks; p67 serious/deadly infection tables and pandemic note;
  p69/p74/p75 titles; and the exact p80 `Hey Marco Babez...EVER!` note.
- No page-124/back-cover publication asset was created by this bounded output:
  both fresh roots have zero p124 decision assets and zero p124 Markdown image
  links; the 121 assets are otherwise closed.
- Final read-only `git status --short --branch` showed only the pre-existing
  worktree governance/source-reconstruction paths; no tracked file was changed
  by this bounded execution, and no Git mutation was performed.

## Files checked and changed

Checked read-only: the sealed packet; assigned plan/context; all frozen script,
contract, source, decision inventory, allowlist and correction-receipt
identities; both fresh roots; candidate/package decisions, pages, assets and
manifests; provenance and QA files; overlay geometry/hash; and final Git status.

Changed by this assignment: all generated files under the two fresh output
roots (candidate 373 files; package 377 files including the 373 inherited
files and four finalizer outputs), plus this receipt. No other file was changed.

## Blockers and next action

Blockers at this bounded execution/QA layer: none. This PASS is execution and
evidence capture only; it is not an independent reconstruction acceptance or a
release decision.

Next action: obtain the fresh independent `gpt-5.5` reconstruction review at
`high` against the immutable v4 candidate/package and this receipt. Keep the
v1-v3 evidence and all frozen inputs immutable; downstream MASTER_EN and later
publication remain pending until that review and required acceptance.

## Receipt identity

Capture this file's detached byte count and SHA-256 after its last write;
embedding its own whole-file hash would change that hash.
