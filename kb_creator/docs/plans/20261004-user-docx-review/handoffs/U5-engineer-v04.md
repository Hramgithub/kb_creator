# U5v04 engineer handoff — two DOCX-only candidates

- Timestamp: 2026-10-04 21:41 UTC / 2026-10-05 00:41 Europe/Moscow.
- Assignment state: bounded engineering complete; candidates structurally validated, **not accepted or released**. Main orchestrator retains integration, rendered visual QA, independent critic gate, canonical state and user-facing decision.
- Orchestrator policy owner: main `gpt-6-sol` / medium per NRI governance. Contributor: `gpt-6-sol` / high engineering. Scoped override: explicit user-approved field-only `art_scope=preserve_original_drawings_only` for these two numeric/name corrections; source-art completeness is **not** assessed. No override for the ordinary pipeline source guard or for Fear's 26-opening art ledger.
- Elapsed time: exact wall-clock time unavailable across context compaction; this bounded implementation and verification completed within the active U5v04 turn. Token use: exact role token accounting unavailable; do not infer precision.

## Scope and result

Source-bound, DOCX-only successors of the reviewed Leningrad and Kremlin DOCX files. Original DOCX/PDF, U7 planning ledger, choices, comments, CSV, Fear candidate, canonical plan/context/status and release state were not modified. No HTML or PDF successor was generated. The adapter sealed 197 approved operations: 146 source-visually checked stat-card characteristic fields (122 Leningrad, 24 Kremlin), 2 source-bound door Strength thresholds, 35 direct skill labels (29 original plus 6 bounded additions), 1 Rybin contextual prose label, 8 accepted Kremlin user labels, and 5 exact Leon/Colin Persuasion consolidation edits. One separate three-node Katerina Strength-drain expression group was applied. A pregen Natural History label was already `Естествознание` and was verified without a no-op edit.

| Book | Candidate DOCX | SHA-256 | Field node groups | Native keeps |
| --- | --- | --- | ---: | ---: |
| Leningrad | `D:/NRI/kb_creator/working/user-review-20261004/leningrad-reader-v01/document.docx` | `CC3A1F96D82121C07938D860EF88186AA33A32199B578D4C7C2DE05F4C83AD23` | 145 | 5 |
| Kremlin | `D:/NRI/kb_creator/working/user-review-20261004/kremlin-reader-v01/document.docx` | `5573888152F7EDAB32D483E4D652FD465694BFBF1764CC708C3EF7C042AA87D8` | 6 | 0 |

Both candidate roots contain `document.docx` only. Desktop-read ACL inheritance was normalized on these exact new roots without changing bytes. Both structural reports state `validated_candidate` and `accepted: false`.

## Changed or checked files

- Reusable implementation: `kb_creator/pipeline/reviewed_docx_revision.py`; exact test suite `kb_creator/tests/test_source_bound_word_fields.py`; user-facing technical note `kb_creator/docs/reviewed-docx-revision.md`. Existing `kb_creator/scripts/revise_reviewed_docx.py` was used, not changed in this step.
- New adapter and frozen evidence: `kb_creator/docs/plans/20261004-user-docx-review/audit/two-book-candidates/prepare_candidates.py`, `accepted-choices-combined-v01.json`, `approved-word-operations-v01.json`, two book-specific `*-manifest-v01.json`, and `leningrad-report-v01.json` / `kremlin-report-v01.json`.
- Source authorities checked by SHA-256 in both manifests: U7 planning ledger, 146/146-pass independent numeric source QA v03, closure, conversion specification, accepted choices v01/v02, review decisions and supplement, comment inventory, and U5v04 packet. Exact DOCX and source-PDF hashes matched the ledger before authoring and again before publication. Every numeric operation ID matched its source-QA record; per-row label/closure/choice evidence is recorded in the approved ledger. No source-physical-page or art-completeness claim was fabricated.

## Verification and preservation evidence

- Focused regressions: `python -X utf8 -m unittest -q kb_creator.tests.test_source_bound_word_fields kb_creator.tests.test_reviewed_docx_revision` → **15 tests passed**. Negative coverage includes missing/incorrect decisions, pair geometry, wrong numeric rule, field-only art-scope bypass, and unsupported picture/page-break/field/hidden target-run topology. A plain `w:br` is allowed only without attributes; target `w:t` alone changes, preserving original child order. Empty `w:t` is checked after its OOXML parse/write round trip.
- The author route re-opened both ZIPs and checked all sealed final text/XML nodes, ordered original paragraphs and drawing occurrences, comment markers, bookmarks, hyperlinks, original part bytes outside the permitted OOXML parts, and source authority hashes before publish. Independent read-only package comparison confirmed identical part sets, same ordered drawings, and byte-identical embedded media and comment parts.
- Leningrad: 1,236 paragraphs before/after, 26 ordered drawing occurrences, 24 unique embedded-media parts byte-identical, four comment-related parts byte-identical. Existing relationship and content-type parts were reserialized with original rows checked intact; only those two plus `word/document.xml` differ at byte level. Kremlin: 320 paragraphs, 14 ordered drawings, 14 byte-identical media parts; only `word/document.xml` differs. Both output hashes match their reports.
- Five Leningrad native keep decisions remain attached to original comment IDs, including Luck 75 and source-handout quotations. Leon and Colin each end with one `Убеждение 40%` pair; exact duplicate `Торг 40%` label/value cells are cleared in place and Colin's surviving 32% becomes 40%. All other table cells/topology remain.

## Exceptions, blockers and next action

No known structural blocker in this accepted finite scope. This is **not** comprehensive 7e mechanics redesign: Resistance Table prose, MP-drain details, source HP and plain Kremlin POW check remain unchanged. Source-art completeness was not assessed under the explicit field-only mode; original art was conserved. Upstream master lineage cannot be reconstructed from the reviewed DOCX. Rendered page QA, any repair decisions, independent `gpt-6-astra` release criticism and final acceptance remain pending with main orchestrator. Main should service-render the two frozen DOCX candidates sequentially, inspect layout and semantic pages, and obtain the independent review before any release decision. The pipeline's mandatory ordinary source guard remains main-owned and unwaived.
