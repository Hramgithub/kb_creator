# U5 DOCX-only Fear engineering handoff (immutable)

- Timestamp: 2026-10-04 21:15 UTC (2026-10-05 00:15 Moscow).
- Assignment state: bounded engineering complete; candidate produced, not accepted. Main orchestration, rendered QA, independent criticism, integration, and user-facing release decision remain with the orchestrator.
- Policy owner: main-chat `gpt-6-sol` at medium under NRI goal governance; this contribution is the `gpt-6-sol` engineering role at high. No orchestration ownership transferred.
- Scoped override: user constrained the successor deliverable to DOCX only. Existing HTML was read-only evidence; no successor HTML, published PDF, OCR, new translation, glossary mutation, or original-input edit was performed. Service-rendered PNG QA is left to main.
- Scope and result: implemented a reusable manifest-bound, reviewed-artifact-preserving DOCX-only revision route; froze exact Fear 26-opener/23-addition manifest; authored one unaccepted Fear candidate.

## Paths and identities

- Reusable code/CLI/tests/doc: `kb_creator/pipeline/reviewed_docx_revision.py`, `kb_creator/scripts/revise_reviewed_docx.py`, `kb_creator/tests/test_reviewed_docx_revision.py`, `kb_creator/docs/reviewed-docx-revision.md`.
- Fear-specific evidence/adapter: `kb_creator/docs/plans/20261004-user-docx-review/audit/fear-candidate/prepare_manifest.py` and `fear-docx-only-manifest-v01.json` (SHA-256 `61CD83812C203E0314ECBED40786657A1AD8B27C1E1365487A1DB330E847C3F2`).
- Separate structural report: `kb_creator/docs/plans/20261004-user-docx-review/audit/fear-candidate/revision-report-v01.json` (SHA-256 `F15B5C4C582E2991E39084ABBAD04B009EA7632A6B74E36363B8F2AABCB5DB53`).
- New candidate: `kb_creator/working/user-review-20261004/fear-reader-v01/document.docx` (SHA-256 `D79AB0EC131D2C6926D868EB037786093F615AEAF122895AA4487254616CF33E`). Its directory contains only `document.docx`; the report explicitly says `accepted: false`.
- Checked original reviewed DOCX: `kb_creator/deliverables/latest/fears-sharp-little-needles/document.docx`, SHA-256 `E8505B99F81A54E02FC1AEA9777C45AE12FDE600A8AB2B2728DDE8F9C0BF8DCD`, unchanged. Checked original source PDF by frozen native-art spec and build input SHA-256 `49CDBAD99DDF5535E5911DBB89D11E2E1D0FC7BABD69DADBCE28A80EC9586888`, unchanged. Audited review decisions, native comment inventory, native art spec, and selected-asset manifest were read as sealed authorities.

## Verification and evidence

- Focused synthetic regression suite: `python -X utf8 -m unittest -q kb_creator.tests.test_reviewed_docx_revision` → six tests passed. Includes absent/stale art selector or paragraph hash, source/manifest midbuild mutation, actual PNG/JPEG content type despite misleading source suffix, independent art coverage, repeated-occurrence collision, exact comment/text binding, ordered old-drawing inventory, and Fear seed 26/23 closure.
- The real build report closes 26/26 source opening obligations: 23 embedded insertions and three explicitly retained existing openers (physical source pages 46, 113, 129). Six comment-bound exact replacements and five explicit keeps were applied. Existing 63 drawing occurrences stayed in order; 63 original media parts and four native comment/thread parts remained byte-identical. Original bookmarks, hyperlinks, native review markers and ordered paragraphs were conserved except declared insertions and replacements.
- Independent read-only ZIP verification found 23 added media members (21 JPEG and two PNG by decoded format), all original non-editable package members byte-identical, candidate hash matching the report, and no HTML/PDF in the candidate directory. Inherited desktop read ACL was normalized on the candidate directory/file using the repository's narrow `normalize_publication_access` helper; bytes remained unchanged.
- The document skill's edit marker was run once immediately before the first real author command. The first normal-sandbox build passed preflight but could not write its staged DOCX due workspace ACL; the identical narrow command succeeded under approved elevation. It left an empty sandbox-created staging directory `kb_creator/working/user-review-20261004/.reviewed-docx-tgyogry7`; it was not removed because no destructive cleanup was authorized.

## Limits and next action

- This is an artifact successor, not lost-source-master reconstruction. The page-74 full-page facsimile retains source English lettering per frozen U3 fidelity exception. No final layout/render finding or release decision is asserted here.
- Main should finish DOCX service-render/layout QA, obtain independent critic review, and decide integration/acceptance. The separate future Leningrad/Kremlin numeric-card work requires a new deterministic unannotated field/table-cell route; this U5 Fear route intentionally requires native comment binding for text decisions.
- Elapsed time: approximately 25 minutes for this DOCX-only continuation (estimate; exact start time was not persisted across context compaction). Token use: unavailable to this contributor; do not infer exact usage.
