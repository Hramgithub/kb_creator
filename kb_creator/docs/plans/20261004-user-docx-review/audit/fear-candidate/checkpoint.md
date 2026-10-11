# U5 Fear candidate checkpoint

The current U4 revision CLI cannot be run under the user's updated output
constraint: it always writes `document.html` along with `document.docx` and
assets. The user now wants a DOCX deliverable only and forbids creating an HTML
successor. No artifact-operation marker was run, no candidate was authored,
and no HTML or PDF output was created.

Read-only intake found 23 materialized selected art files plus their manifest
under `working/user-review-20261004/fear-source-art-v01/`, six explicit Fear
replacements and five Fear keeps in `audit/review-decisions-v01.json`, and 26
story links in the current HTML TOC. The first opener's Word bookmark is unique;
its heading, byline and tag group occupy body paragraphs 123–125 (zero-based
in this inspection). This is a topology example, not a frozen placement table.

Minimal revised implementation scope: create a separate DOCX-only successor
route while the U4 dual-output module remains under independent review. It
would consume the reviewed Word package, immutable source PDF, frozen selected
images and explicit decision manifest. The independent ledger would require
all 26 source openings, merge the three retained openings with 23 new scenes,
and verify all 63 original drawing occurrences in order. It would apply six
exact Word replacements and record five explicit keeps, insert each selected
scene after an exact in-story Word group-end paragraph, preserve native comments
and other OOXML parts, and produce only a new DOCX plus JSON evidence in this
audit area. The existing HTML can be used read-only to check anchors; it must
not be regenerated. A separate service render may be used for layout QA, but
no published PDF is part of this candidate.

The main orchestrator must issue a revised bounded engineering packet before
implementation. No acceptance or release decision is implied.
