# Current checkpoint

The user approved a separate post-package revision and requested an updated
PDF in addition to committing the corrected DOCX. The edited bytes are now
preserved at `working/number-7-dream/revisions/20260919-post-package-docx-01/submissions/Number_7_Dream_RU.reviewed.docx`
(5,167,147 bytes, SHA-256 `BBF475FC50E0465CE6997BC2F819833B00AE4B08AE6F7C7A689C9DACA74E520D`).
The old production DOCX was restored from HEAD only after this verified copy;
the frozen package's copied verifier again passes its original manifest SHA.
The reusable `publication revise-docx` builder now produced a self-contained
successor candidate under `working/number-7-dream/revisions/20260919-post-package-docx-01/candidate/`.
The first attempt exposed a reusable projection bug: inherited base `evidence/`
already existed before `evidence.mkdir()`. The builder now preserves that
directory, fails closed on conflicting derived evidence, and has four passing
focused regression tests.
`publication verify-revision` passes: 30 pages, exact DOCX SHA above, PDF
SHA-256 `C3DD457412567A1EB89AF8DA27BE973F0B84993DE0B8CB79A8BC1C1CC84E3B4F`,
state `awaiting_visual_review`, release `not_reviewed`. The independent
`render_docx.py` export also has 30 pages and page-by-page identical extracted
text, but is not byte-identical to the candidate PDF; its PNGs use a higher
resolution. All 30 independent page PNGs were inspected. Comparing extracted
PDF text with the frozen base shows
changes only on pages 23–24: the edited DOCX restored the handout-2 letter.
Pagination now leaves the handout-4 label alone near the foot of page 23 while
its body starts on page 24. This needs the user's visual decision; do not
alter the exact user-edited DOCX or record acceptance without it. No commit or
push is implied by PDF generation. A tracked preservation checkpoint now holds
byte-identical copies of the reviewed submission and PDF preview under
`inputs/number-7-dream/revisions/20260919-post-package-docx-01/`; both are
Git-LFS-bound and explicitly labelled as not accepted. The full verified
successor remains in ignored working state until the user's pagination
decision.
