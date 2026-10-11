# Terra remediation packet — Viral Step 6A reconstruction finalizer

## Boundary

Remediate the first finalizer implementation under the original engineering
packet. Keep the same Terra/medium role and the same two implementation files.
The first receipt is immutable. Write one new receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_finalizer_remediation_20260901.md`

Do not touch any other file or any real v3/candidate/package. The PDF operation
marker already succeeded exactly once; do not run it again.

## Blocking findings to close

1. The current regex does not match the required identities `*Handout #1*` etc.
   Its fixture incorrectly uses `# Handout 1`, hiding the defect. Frozen v2 pages
   87-103 establish the canonical representation. Parse only an exact italic
   identity line of the form `*Handout #<label>*` (allow surrounding whitespace
   only) inside the contract-declared `player_handouts` page range.
   Require exact full-label multiset `1,2a,2b,3a,3b,4..39`, unique full labels,
   and unique numeric ordinals exactly 1-39. Record each label's source page in
   provenance. Page 82 legitimately has none.
2. Asset closure checks manifest entries but does not reject undeclared extra
   files under `assets/`. Require exact declared-vs-actual relative-path set,
   hashes, and Markdown link closure without absolute or candidate-escaping
   paths.
3. Provenance currently embeds an inventory list but not the required portable
   identity. Add candidate file count, byte count, root hashes, and the ordinal
   trailing-LF inventory digest over
   `path<TAB>bytes<TAB>UPPER_SHA256<LF>`. Record the exact algorithm/version.
   Add selected-overlay PDF SHA-256/bytes after it is written.
4. Cross-check each decision's `selected_blocks` and `unresolved` against the
   corresponding merge-provenance page, then resolve each selected block against
   frozen comparison with matching source page. Reject mismatch, unknown view,
   duplicate raw reference or unresolved record.
5. Validate each layout PDF page domain before building, validate selected
   view/page domain exactly, and after reopening the output compare media box and
   rotation to the selected input layout page and the contract media-box/rotation
   requirements. Do not reopen the source reader 124 times.
6. Keep all seven named gate rows honest and deterministic. Successful package
   status remains only `candidate_ready_for_reconstruction_review`. Failed input
   must return a concise deterministic error list/nonzero exit and leave no output
   root or stage residue; it must never emit a partially passing package.
7. Rewrite the compressed one-line implementation into clear functions and
   readable control flow consistent with repository Python guidance. Preserve
   deterministic UTF-8/LF JSON and no timestamps.

## Focused tests

Use exact production-shaped italic identity lines containing `#`. Add direct cases covering:

- success with 41 full labels and numeric ordinal closure 1-39;
- missing/duplicate label and identity without `#` rejection;
- page/decision/marker missing or duplicate domain;
- decision/provenance selected-block mismatch and unknown view;
- unresolved record;
- missing/corrupt/extra asset and escaping/broken Markdown link;
- bad overlay preference, duplicate/missing selection and short layout;
- role gap and overlap;
- source hash/bytes/pages mismatch;
- existing output refusal and no leftover stage on failure;
- deterministic provenance/QA and selected overlay page order.

Keep this a compact focused file (roughly 10-20 direct/parameterized test nodes),
not a selector matrix. Run only this file, `py_compile`, and `git diff --check`.
Do not run MinerU, materialize real content, or run 371/119/490.

## Receipt

Record exact commands, exit codes, collected/pass count, new script/test hashes,
first-receipt hash, confirmation that the marker was not repeated, and a finding-
by-finding closure table. Return only a compact summary.
