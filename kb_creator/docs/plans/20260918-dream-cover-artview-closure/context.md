# Number 7 Dream cover and ArtView closure context

## Observed defect

Publication run14 declares source page 1 as `cover`, but
`frontmatter_manifest.json` records `cover.asset = null`, and the final HTML
page-001 contains only reconstructed title/byline text.

The accepted reconstruction decision for page 1 has semantic role `cover` but
`assets: []`. Its three MinerU comparison views also contain only text blocks.
Consequently the checked-in ArtView source graph and profile contain 19 rows
from pages 4-26 and no page-1 row.

This is not supported by the immutable source PDF: `pdfimages -f 1 -l 1 -list`
reports page-1 image objects including 1200x900, 1837x2450, and 455x222 rasters
plus small mask/line objects. The full-page cover is therefore discoverable.

The earlier M3 publication-authority design is the direct origin of the
omission: it explicitly instructed the author to mirror "only the 19 assets
referenced by accepted Markdown". That coupled discovery to reader placement
and intentionally omitted every source visual not already represented in
Markdown. The live tool then proved only that hand-authored subset.

Independent page geometry confirms that the cover is a composite publication
unit, not simply the largest embedded raster: page 1 includes a full-page photo,
a separately placed logo, a thin image strip, source text/vector content, and
an additional raster placed mostly outside the visible MediaBox. The required
cover candidate is therefore a deterministic clean full-page render. The raw
objects still belong in the sealed discovery ledger with component, mask, or
clipped disposition; none may vanish merely because Markdown omitted it.

## Confirmed boundary failure

The active ArtView v3 profile is row-driven and was authored exclusively from
accepted reconstruction assets. It can extract/audit candidates for configured
rows, but it does not independently prove that the configured rows exhaust the
source PDF visuals. Reconstruction `asset_closure` only closes declared assets,
so a visually rich page with `assets: []` passes. Stage 40 validates the cover
page role/order but its normalized policy carries only `source_page`; it also
allows a manifest whose cover asset is null. The prior run14 QA therefore
proved internal closure of an incomplete declaration, not source-cover
fidelity.

## Required correction direction

Visual discovery must be source-PDF-backed and independent of reader Markdown.
Reconstruction/MASTER references remain placement authority; ArtView is the
human decision surface for source visuals, including a deterministic full-page
cover composite where the cover is a multi-object page. Stage 40 must consume
an explicit accepted cover binding and fail closed when that binary is absent.

## User-confirmed execution contract

ArtView is one deterministic tool invocation, not an editorial assembly step.
Its checked-in profile may bind immutable authorities and extraction settings,
but it must not contain an authored row list, authored page-role map, or a
scenario-specific exclusion list. A single Stage-30 invocation must discover
the PDF image occurrences, reconcile them with the already accepted MASTER_RU
asset references, render the composite cover when required by accepted
reconstruction semantics, and produce the complete review bundle. Human
judgement begins in the generated ArtView UI and never before it.

The regression existed because three incompatible generations remained live:
the legacy PDF extractor, the v3 copier of 19 authored rows, and an unfinished
page-render successor. The control plane selected the v3 copier, so earlier
fixes in the extraction path did not govern the actual Number 7 Dream run. The
remediation therefore replaces the branch at the contract/adapter boundary;
it is not a one-off cover insertion.

## User-confirmed ArtView interaction contract

The image cards are the decision control. Clicking the current binary or one
candidate is the explicit human review action: the selected card is outlined
in green, the row status becomes `Выбор сделан`, and the progress count
advances. A separate binary-choice field, notes field, and human-review
checkbox are redundant and must not be rendered. Presentation parameters stay
available but do not invalidate an already explicit image choice. The exported
decision document keeps `reviewed: true` and an empty `notes` string for schema
compatibility, and its schema identifier comes from the bound candidate
manifest rather than a hard-coded UI version.

## Stage-40 closure after accepted ArtView decisions

The user exported a closed run18 v4 decision document with 20/20 reviewed and
zero unresolved rows. Its SHA-256 is
`8504FE1DF206A25FA30B7EEAE90F0ED6FFFD6CF0F7A8408BE5146C19D86F07B0`.
Stage 31 accepted it, while the first Stage-40 attempt exposed an ordering bug:
the adapter replaced page 1 before semantic projection and thereby changed the
accepted MASTER_RU line topology. The systemic correction projects semantic
spans first, rejects a cover page that owns such a span, and then replaces the
cover.

The fresh-run bridge also exposed that `rebind-decisions` handled only v3. It
now strictly supports v4 by checking both profiles, exact ordered visible rows,
decision contracts, actual binary inventories, and selected-binary identity.
No user decision is inferred. A later Stage-40 guard incorrectly classified
the renderer-owned page marker and `Cover` figcaption as retained source prose;
the validator now ignores exactly those known chrome elements while still
rejecting any other visible cover text.

Fresh run `20260918-publication-21` binds all corrections. It reproduces the
accepted MASTER_EN and MASTER_RU hashes, strictly rebinds the user's 20 choices,
completes Stage 31, and builds the Stage-40 HTML candidate. DOCX/PDF remain
closed pending exact HTML acceptance.

User review of run21 found that renderer-generated image `alt` labels were also
shown as visible `figcaption` text (for example, `Исходное изображение со
страницы 17`). The source of the defect is the generic Markdown image renderer,
not ArtView or either accepted master. The remediation adds a closed
`authored_only` figure-caption policy: known generated labels are hidden while
their accessibility `alt` values and any nontechnical authored captions remain.
Run21 is retained as immutable feedback evidence; a versioned successor config,
contract and publication run are required after the renderer identity changes.

The successor is `20260918-publication-22`, portable identity
`C0484A376CCA67692CB3946C3D48AE513CAAF8CDA4D9F8291DB66B7C5B011C1C`,
under versioned publication config v3 and contract v10. MASTER_EN and MASTER_RU
are byte-identical to their accepted hashes; all 298 translation units were
rebound as `exact_source`; the 20 accepted ArtView choices were strictly rebound
with zero inferred decisions. Stage 40 produced a 153,550-byte HTML candidate,
SHA-256 `D3DBE3BE8CACAE9C7317F787150C9CD34932A71D04BE4C1BFDE73D506DA5B537`.
It is byte-for-byte equal to run21 after removing exactly its 20 generated
technical `figcaption` elements. All 20 image `alt` values remain; producer QA
passes with 85 headings, 26 source pages, 20 resolved images, 18 source-TOC
entries, seven statblock cards and zero findings. Focused regression suites pass
`157 passed, 13 skipped, 5 subtests passed`.

User review of run22 then exposed a preserved-source-TOC normalization defect:
the renderer replaced each source entry's display level with the H1/H2/H3 level
of its resolved target. Appendix links therefore became bold uppercase H1-style
items even though the printed source contents is a flat list. The reusable
renderer now keeps source TOC presentation hierarchy independent from link
targets. Stage 40 accepts a closed `display_mode` plus optional per-entry
`display_level`, projects the rule into the renderer, and rejects a final DOM
whose `data-toc-layout` or `toc-level-*` sequence disagrees. The flat layout has
an explicit non-uppercase peer style rather than borrowing the ordinary H1
TOC style.

Versioned config v4 declares `display_mode = "flat"`; contract v11 binds that
config. Run23 proved the source-level hierarchy correction but is intermediate
evidence because the first implementation lacked a distinct flat CSS style.
Fresh run `20260918-publication-24`, portable identity
`6C930320298EBD97CC0E77BD603D6B089EE0FB1F3F593069D363B3672D210643`,
reproduces the accepted MASTER_EN and MASTER_RU bytes, rebinds all 298
translations and all 20 accepted ArtView decisions, and reaches Stage 40. Its
153,683-byte HTML SHA-256 is
`774F22BC2D1FF55BBCEF22ED5BC8539508F265A01D34E7AC8C6E87CE82AB7166`.
Producer QA passes with 18 ordered source-TOC links, 18 peer `toc-level-1`
entries under `data-toc-layout="flat"`, the explicit non-uppercase flat style,
20 images, zero visible figcaptions, seven statblock cards, and zero findings.
The focused renderer/adapter/control-plane/contract suite passes `208 passed,
1 skipped, 5 subtests passed`. HTML acceptance remains explicit; DOCX/PDF stay
closed.

Read-only browser QA of the exact run24 HTML is recorded in
`handoffs/A13-run24-orchestrator-browser-qa.md`. It visually confirms the
full-page cover, credits/source-TOC order, 18 peer TOC entries, neutral
Appendix A statblocks, zero page-18 blockquotes, and zero visible generated
figcaptions. This evidence does not replace independent release review or the
user's explicit acceptance of the exact HTML hash.

## ArtView previous-config import restoration

The strict import workflow existed in the legacy ArtView page but was omitted
when the active simplified PDF-driven v3/v4 review UI replaced it. The defect
was therefore an implementation-branch regression, not a missing scenario
configuration. The active `_v3_review_html` generator now owns a modal import
workflow for both v3 and v4. It validates the closed document shape, scenario
and schema, recomputes the canonical SHA-256 seal, validates every row and
candidate, and distinguishes exact current bindings from an older compatible
candidate. Exact imports restore review closure; compatible imports preserve
only valid choices/presentation and reset every `reviewed` flag.

Fresh run `20260918-publication-25`, portable identity
`33EC6B5D68244F5BF4950451D1F08A5D9A892EECC46D0B1CDC4D9FE0F01C4211`,
reproduces accepted MASTER_EN SHA-256
`C3B4F13E3E43B2422704F1A7BCF61A5CF1762191B474FAAE5C4C4243289367AA`
and MASTER_RU SHA-256
`904133D5057172C404D28F3BCF2A5E4C578304A59382512D1B31FC56AE0FDAB2`.
All 298 translation units transferred as `exact_source`. Stage 30 rebuilt the
20-row ArtView bundle with the import modal. A strict v4 rebind produced the
current-candidate import file with 20 decisions and validation passes 20/20.
Browser QA imported it through the modal, observed the exact-match summary,
then restored `Выбрано 20/20`, all `Выбор сделан` states, and the enabled
accepted-export button. The current gate is the user's reviewed/exported run25
accepted JSON; later stages remain closed.

## Run25 accepted ArtView and Stage-40 successor — 2026-09-19

The user supplied a new accepted ArtView export and directed continuation. The
newest export in Downloads was copied without modifying its bytes to run25
`submissions/artview/artview-decisions.accepted.json`, SHA-256
`6EE7217A9B995EC3143A022ED6D6D3360CD19F3AB44C7A8169CE6222DA875BED`.
It passes strict v4 validation: 20 decisions, 20 reviewed, zero findings. Its
20 binary and presentation choices are semantically identical to the strict
run25 rebind used for import; the distinct file hash reflects export
serialization. The run-local acceptance receipt is
`acceptance/artview.acceptance.json`, SHA-256
`FCF4512D0E59B870C60E1C615623EF0151E6B4631497D90ADBCD2D1AB97E0D3D`.

Stage 31 completed with `ready_for_html_candidate`. Stage 40 completed with
`awaiting_html_acceptance`; its HTML is 153,683 bytes and SHA-256
`774F22BC2D1FF55BBCEF22ED5BC8539508F265A01D34E7AC8C6E87CE82AB7166`.
All 21 Stage-40 artifact files, including 20 images, match run24 byte-for-byte.
Producer QA reports 26 source pages, 85 headings, 18 source-TOC links, seven
neutral statblock cards, 20 resolved images, 20 suppressed generated captions,
and zero findings. Local HTTP checks return 200 for both HTML and cover; output
ACL inheritance is active. The prior read-only run24 visual QA applies to the
identical HTML and asset bytes. The next gate is explicit user acceptance or
correction of this exact run25 HTML; no DOCX/PDF or release step is authorized.

## Accepted HTML and DOCX successor — 2026-09-19

The user explicitly accepted run25 Stage-40 HTML SHA-256
`774F22BC2D1FF55BBCEF22ED5BC8539508F265A01D34E7AC8C6E87CE82AB7166`.
Run25 `acceptance/html.acceptance.json` records that decision. Stage 50 built a
5,216,339-byte DOCX but its transient Word COM review export failed. A direct
diagnostic of the bound exporter returned `0x80070520`: no valid Windows logon
session for the Word COM class. The failed Stage-50 tree was quarantined by the
control plane. Run25 is preserved; it was not edited or resumed under a new
engine.

Successor run26 bound repository-local LibreOffice from the outset. It
reproduced accepted MASTER_EN and MASTER_RU bytes, rebound 298/298 translation
units as `exact_source`, strictly rebound the 20 accepted ArtView decisions,
and reproduced the accepted HTML plus all 20 assets byte-for-byte. Stage 50
passed, but visual QA exposed a separate shared DOCX-builder regression: the
explicitly flat source TOC was uppercased and bolded because `add_toc_entry`
treated every level-1 numbered entry as a primary hierarchical heading. The
source HTML had already corrected this. Run26 is immutable defect evidence.

The reusable `production_docx.py` now treats explicit
`data-toc-layout="flat"` entries as equal-weight peers and preserves their
source display text; unspecified legacy and hierarchical layouts retain their
previous policy. `patch_existing_docx` rejects drift between an explicit flat
HTML TOC and DOCX visible text. The combined publication-control and DOCX
suite passes `42 passed`, including the explicit-flat and text-drift cases.

Fresh run27 portable identity
`D9F683E5A04777FD4495F45CB13FB27653752936778E637A4611D6CDA19F9A04`
binds the corrected builder and repository-local LibreOffice. It again
reproduces the accepted masters, 298 exact translation units, 20 reviewed
ArtView decisions, and the accepted HTML/20 asset bytes. Its Stage-50 DOCX is
5,216,255 bytes, SHA-256
`BEE0CFB92A87E73C4EDF95BAB3600A62263AF090F4750DEB272CFB08F79601F5`.
The build reports 20 images, 18 TOC entries/bookmarks/internal links and 12
callouts. The transient render has 34 PNG pages, zero near-blank/orphan
signals, and leaves no PDF in Stage 50; an independent bundled renderer also
produced 34 pages. All 34 stage page images were visually inspected, including
the corrected flat TOC on page 2. Output ACL inheritance is active. The
page-22/23 Mi-Go stat block spans a page boundary, and the image-heavy player
character section has partially filled continuation pages; these are retained
for user editorial review rather than silently changing the accepted source.
The active gate is explicit user acceptance/correction of run27 DOCX. No
Stage 60 PDF, production package, release, commit, or push is authorized yet.

## Reviewed DOCX successor and PDF gate — 2026-09-19

The user edited run27 Stage-50 DOCX in place and directed continuation. Its
current bytes (5,349,133; SHA-256
`C29A5569820A3D2734F28089619F1BC273E1013A8CD040439C3F58899CE9F5BE`)
do not match run27's original sealed Stage-50 manifest, so run27 cannot be
accepted or resumed as-is. The generic Stage-50 `reviewed_docx` authority now
imports a run-local reviewed submission byte-for-byte after validating OOXML
and rebuilding the accepted-HTML baseline for QA; optional input identity is
enforced by the control plane and offline package verifier. The selected
control-plane regression suite passed 44/44.

Fresh `20260919-publication-28`, identity
`B951C74B86A46415BFD318A3408D00560E90717D454F94A0BDC96101B9AA4F3B`,
rebound 298/298 translation units as exact source, rebound 20/20 ArtView
choices, and reproduced accepted MASTER_EN, MASTER_RU and HTML SHA-256
`774F22BC2D1FF55BBCEF22ED5BC8539508F265A01D34E7AC8C6E87CE82AB7166`
exactly. Stage-50 input is `submissions/docx/Number_7_Dream_RU.reviewed.docx`;
its output DOCX has the same reviewed SHA-256. All 30 human-edited DOCX page
renders were visually inspected; render QA found no near-blank/orphan pages,
and `acceptance/docx.acceptance.json` records the directed continuation.

Stage 60 freshly exported a 2,913,242-byte PDF with SHA-256
`7AC8C2A9F1964AEADC398206881B43DED7F7C8E8CFB372D35269480886F6D5C3`.
Its 30 page PNG hashes are identical to Stage-50 review PNGs, with no
near-blank/orphan signals; export reports the exact accepted DOCX input hash.
The only current gate is the user's explicit PDF review. No Stage-70 package,
release, commit or push is authorized by this checkpoint.

## Second reviewed DOCX revision and PDF successor — 2026-09-19

The user edited the run28 Stage-50 DOCX after its acceptance and explicitly
requested another PDF build. Its new 5,350,241-byte SHA-256 is
`16ED29E537C6E87553A5BA4E8CB47725B96C2AE43E5F4ECA3E078716950970D5`,
different from run28's sealed `C29A5569...` acceptance. Run28 was not
resealed or resumed. Fresh `20260919-publication-29` has portable identity
`D2E6E189776332AA1706808894EE2E38868A68889988F7716EBD11C2BF884804`.
Its MASTER_EN and MASTER_RU bytes match earlier accepted versions; all 298
translation units transfer as exact source, 20 ArtView choices strictly rebind,
and its HTML plus all 20 assets match run28 byte-for-byte. The updated DOCX was
copied as a run-local `reviewed_docx` submission; Stage 50 output is
byte-identical and its acceptance records the user's request to continue.

The DOCX still renders to 30 pages; only pages 20 and 21 changed visually.
The user moved Appendix A to the start of page 21. Both affected pages were
visually inspected and show no clipping; the other 28 page PNG hashes are
unchanged. Stage 60 made a fresh 2,914,792-byte PDF, SHA-256
`B39214DD4CCD084A0867697F883E7B08CEEBAD6EF3B66D5CC5EB04C41D399EBD`.
Its 30 rendered page PNG hashes exactly equal the Stage-50 DOCX review render;
neither render has near-blank/orphan signals. Export evidence binds the exact
updated DOCX hash and records a fresh all-pages LibreOffice export. The PDF is
awaiting explicit user review; Stage 70 and release remain closed.

## Accepted run29 PDF, verifier defect, and run30 gate — 2026-09-19

The user explicitly accepted run29 PDF SHA-256
`B39214DD4CCD084A0867697F883E7B08CEEBAD6EF3B66D5CC5EB04C41D399EBD`;
`acceptance/pdf.acceptance.json` records that exact decision. Stage 70 built
the package, but Stage 80's copied standard-library verifier failed with
`ArtView decisions are not accepted`. The package's decisions are valid,
sealed, 20/20 reviewed v4. The copied verifier had a hard-coded v3 schema
constant. The live orchestrator verifier accepted the package, confirming the
gap was in the copied self-contained verifier, not in the PDF or decisions.

The shared copied verifier now accepts closed schemas v3 and v4 while retaining
shape, seal, reviewed-row, and acceptance-chain checks. Two-version
regression tests reject draft decisions and accept closed ones; the control-
plane suite passed 41 tests. The corrected live verifier also passed the run29
package read-only. Run29 Stage-70 artifact remains immutable defect evidence;
it was not patched in place or represented as offline-verified.

Fresh run30 identity
`BB42B89B11E13357F865B4582A5C53AC8F5A3458C3E128F2D16BC39D4E3C25F6`
binds the fixed script. Accepted MASTER_EN and MASTER_RU hashes, 298 translation
units, 20 strict ArtView decisions, HTML and 20 assets, and exact reviewed DOCX
SHA-256 `16ED29E537C6E87553A5BA4E8CB47725B96C2AE43E5F4ECA3E078716950970D5`
were preserved. The 30 Stage-50 DOCX render PNGs are unchanged. Run30's fresh
Stage-60 PDF has SHA-256
`9D9E617D263AF3F81A772E575A394E362A46429ED248D77745A9B7618B5D7875`.
Its 30 page PNGs exactly match the accepted run29 PDF PNGs, but the PDF bytes
differ (including export metadata/font streams). The exact-byte PDF acceptance
cannot be rebound. Run30 is stopped awaiting explicit user acceptance of this
new PDF before Stage 70, Stage 80, or release review.

## Run30 verified production package — 2026-09-19

After the exact run30 PDF confirmation request, the user instructed package
assembly. `acceptance/pdf.acceptance.json` records that direction against PDF
SHA-256 `9D9E617D263AF3F81A772E575A394E362A46429ED248D77745A9B7618B5D7875`.
Stage 70 assembled the package, and Stage 71 executed the package's copied
offline verifier successfully. The frozen package is at
`outputs/70-production-package/artifacts/package`; its manifest SHA-256 is
`930965C745E0889B931CED46D738C94A0DCEB393F38F20CD913CFF42BC60B2C8`.
It contains 212 files, including the HTML reader, 20 local assets, exactly
one PDF, the reviewed DOCX and its submission, accepted masters/ArtView,
configs, evidence, and pipeline/schema snapshots. The verifier reports
`candidate_for_release_review`, `release_state: not_reviewed`, 20 resolved
local HTML references, and one PDF. Package HTML, PDF and DOCX hashes match
the accepted run30 candidates; package ACL inheritance is active. No
independent release decision, commit, push or deletion was performed.
