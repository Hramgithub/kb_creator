# Innsmouth Direct Publication Context

Goal ID: `20260826-innsmouth-direct-master-ru-publication`

Last updated: `2026-08-30`

## Canonical state

The promoted strict-pipeline package is the sole English production authority:

`kb_creator/inputs/innsmouth/master_en/accepted_20260830_r2/MASTER_EN.md`

Identity: `127769` bytes,
`31F67A2865BF00A48F197333A162AD56AA0F56061068D3BFD6B564591F9AA3C2`.
Its 36-file package contains path-independent QA, a deterministic acceptance
manifest and 33 assets, including the source cover. Repository inventory
SHA-256:
`D244FBE98E65119826A387F62B4A11ACB331935CB5D157D5656FF9B26A267241`.

The permanent Russian publication authority has now been created only through
the tested promotion gate:

`kb_creator/inputs/innsmouth/master_ru/accepted_20260830_r2/MASTER_RU.md`

Identity: `189302` bytes,
`E9A0AF27BEFE56630E1DBF24CD63EB9C8768706FEAE4C4DB1836E3175D4DED8E`.
Its 34-file package contains the 32 selected canonical EN reader assets and the
acceptance manifest `87B3B867895209D8444F5B7E940EE6E14BECE3C79D810F35C92BD5D4FA6ED412`.
Asset inventory SHA-256:
`849C8238A9165EADC8A796B6A2501C84E9CD220F303CD70E46940FAF6C1E3019`.

The `2026-08-29` localhost browser audit found one cross-layer defect class:
16 heading-class anchors were bound to body prefixes. The EN target table now
binds them to existing headings and validates every `nri-h-*` target except the
single documented body-only `The Innsmouth Terror` entry. RU promotion
reproduces the corresponding 16 Russian heading placements. The corrected
pipeline also implements the approved handout reader flow: body duplicates of
Handouts 1-a and 2 are suppressed, the Handout 2 Keeper note is conserved in
the appendix, all eight narrative references link to appendix targets, Handout
2 is consolidated to one block, and five decorative handout crops are excluded. The
`2026-08-30` successor checkpoint is not yet committed or pushed; prior critic receipts
bind the superseded hashes and remain historical evidence only.

## User decisions

- The above `MASTER_EN.md` was explicitly accepted and promoted on
  `2026-08-29`.
- The required chain is direct:
  `MASTER_EN -> new MASTER_RU -> HTML -> PDF`.
- Historical RU v6, old cleaned EN and the historical bridge are excluded.
- The earlier compiler-like translation-unit design was overengineering. It was
  never accepted, committed or used to create Russian prose, and its untracked
  implementation/evidence files were removed on `2026-08-27`.

## Accepted RU source and promoted result

The first complete direct translation candidate exists at:

`kb_creator/working/innsmouth_direct_master_ru/MASTER_RU.md`

- physical lines: `1442`;
- bytes: `195422`;
- Unicode characters: `117955`;
- SHA-256:
  `BAF53B8E20AA91D3124AE83C7D3A533F4D9D16B9F104AB47B93995B048C81FC9`;
- state: `USER_REVIEW_COMPLETE`, retained as the exact promotion source.

The promotion gate pins that source identity, first realigns exactly 16 existing
semantic anchor lines to the corresponding Russian headings, then applies the
already approved Hobby World skill synchronization plus deterministic handout
and front-matter projections. The current promoted r2 successor has 32 ordered
image references, 51 tables, 152 headings, 52 anchors, 86 fragments, zero broken fragments, and
zero `mineru-page`/`table-evidence` comments. The glossary is
bound at `11884` bytes, SHA-256
`BE7CCE74993263983670FF68459805CCB49DE873B1EB5B1B95E85442FF223304`.

The first independent RU promotion release review returned
`REMEDIATION_REQUIRED` for one P1: package verification did not pin
release-significant manifest metadata. The verifier now pins the complete
acceptance manifest at `3393` bytes / SHA-256
`D1548C72B8DC7F0A713B1C36807F018F88434FF7CBDF59E51254A4DA64A7613F`
and requires exactly the then-current 33 canonical asset filenames with no directories or
extras. Negative tests cover metadata-only manifest mutation and an extra
asset. Post-remediation evidence is `6 passed` focused and
`72 passed, 6 skipped` for the explicitly listed EN/RU/Keeper suite. Fresh
independent closure review returned `APPROVE` with no P0/P1/P2 findings.

It was translated in four consecutive non-overlapping source ranges and then
concatenated without normalization. The first independent QA returned
`REMEDIATION_REQUIRED`; its editorial findings were remediated directly in the
single candidate. The second QA found one ordered Handout 2 tail-boundary
defect hidden by aggregate counts. That order was corrected without changing
any other block. Final QA then found one remaining visible `Boston`, corrected
to `Бостоне`. A fresh `gpt-5.5` critic then found three visible `Orne` residues
and one agreement error in a closing handout; those four lines were corrected.
During user review, the missing sibling `assets/` directory was found and
restored by copying the 38 canonical EN-package assets byte-for-byte. A full
reference check proves 38 ordered RU references, zero missing files and zero
SHA mismatches. Character-count review exposed a skill-check case-agreement
class; all occurrences were corrected, and the exhaustive known-skill scan now
returns zero uninflected labels after forms of `проверка`.
The final ordered line-by-line gate proved exact blank mask and structural-
position parity for the pre-cleanup hash; final QA verdict was `PASS`, and
critic verdict was `APPROVE_FOR_USER_REVIEW`. User review then removed all 51
`table-evidence` and 43 `mineru-page` comments from RU only. They remain in EN
as reconstruction evidence and are not reader content. The user completed the
full reading review and accepted the candidate's reader text and structure on
  `2026-08-29`. The tested executable freeze/promotion completed on the same
  date. The user authorized the scoped save-point; commit
  `bd0da472d63f58bc348e619e7393bcf6652a46e1` was pushed directly to
  `origin/main`, and the frozen RU verifier passed again after push.

Those `38`-asset figures describe the pre-handout user-review draft. The later
approved handout projection removes the body-only duplicate Handout 1-a
signature asset together with the duplicated letter; the current promoted
package initially had 37 assets without losing appendix content. The final
text-only handout policy also removes the remaining two seals and two signature
crops, leaving 33 reader assets while `RECONSTRUCTED_EN` retains the evidence.
The `2026-08-30` successor removes the final remaining Miskatonic letter-seal
crop at the same editorial boundary, leaving 32 reader assets without changing
translated prose.

## Accepted r7f/r6 publication successor — 2026-08-30

The user's PDF review superseded r6b/r5 with four corrections assigned to
their owning pipeline layers:

1. `build_innsmouth_master_en.py` removes the complete source `CONTENT
   WARNINGS` section at Stage C.
2. `build_innsmouth_reconstructed_en.py` recovers the source cover at Stage B;
   Stage C retains it, and HTML overlays the Russian title while masking the
   source English title and lower service logos.
3. `freeze_innsmouth_master_ru_repo_input.py` removes the authors/credits block
   during deterministic RU projection; it is absent from the promoted r2 RU
   package rather than hidden only in generated HTML.
4. `build_innsmouth_html_from_master_ru.py` assigns all 21 non-full-width
   illustrations to right floats and restores that float explicitly in print
   media. The title image separately overrides the generic `120mm` print-image
   cap; an explicit stacking context keeps the Russian overlay above the masks.

Accepted HTML source candidate:

`kb_creator/working/innsmouth_direct_html/accepted_20260830_candidate_r7f/`

- HTML: `223459` bytes, SHA-256
  `040C7AF42A76241B3BC280350C0151096CF81E5F9A9194E6F5003B0388E4EF39`;
- 32 unique image references, zero missing/unused assets, 51 tables, 22
  stat-block cards, 52 stable anchors, 86 fragments and zero broken targets;
- one source-art title page, zero credits sections, zero content-warning
  sections, 11 full-width figures and 21 right-float figures;
- the user accepted r7f and the freeze gate promoted it to
  `kb_creator/inputs/innsmouth/html/accepted_20260830_r2/`;
- its deterministic manifest is `6966` bytes, SHA-256
  `B0ADDD901CCD0DED10D84D331B3F168987070558641D374F13ABC30852E6D7E6`.

Final PDF candidate built only from that permanent HTML package:

`kb_creator/working/innsmouth_direct_pdf/accepted_20260830_candidate_r6/The_Innsmouth_Terror_RU.pdf`

- `11566429` bytes, SHA-256
  `8D79F72CB61626B05DE7EC000E140FA0C893C6B3D2DC693A64DF45AF756AE202`;
- 46 A4 pages, 97421 text characters, 32 image XObjects, 88 internal links,
  zero empty pages and zero structural findings;
- physical front matter is title page 1, introduction page 2, TOC page 3 and
  body start page 4; warnings and credits are absent;
- all 46 final 120-DPI renders are pixel-identical to the accepted r7f preview
  render set; pages 1, 7 and 46 were also inspected at full size.

The user directed the project to treat successful PDF QA as acceptance. The
exact PDF is frozen at
`kb_creator/inputs/innsmouth/pdf/accepted_20260830_r2/`; its acceptance
manifest is `1664` bytes, SHA-256
`3477760E4C49892D54819CBB7D18A57F309533176217C4D43FAA5F6756950105`.
Final scoped EN/RU/HTML/PDF/renderer regression is `74 passed, 11 skipped`.
Broad test collection still stops on 15 archived page-proof/raw-authority
imports whose modules are absent from this branch; that historical collection
problem is outside the publication implementation.

## Historical direct HTML review candidate — 2026-08-30

`scripts/build_innsmouth_html_from_master_ru.py` is the direct downstream
route. It re-verifies the frozen RU package and its canonical EN/glossary
provenance, copies the exact 192079-byte promoted `MASTER_RU.md` plus all 32
assets into a self-contained generated working package, and invokes the generic
Markdown-to-production-HTML renderer plus its tested deterministic presentation
pass. Historical v6 inputs, the old EN/RU bridge, intermediate `KeeperBook`,
duplicate generated TOC and manual HTML edits are excluded.

Current review package:

`kb_creator/working/innsmouth_direct_html/accepted_20260830_candidate_r6b/`

- HTML: `225985` bytes, SHA-256
  `375A98E69FD763C85465A9E1D64D45885D475AFFDFCBBB5AC9862FD36ED4BEAA`;
- 52 stable anchors and 86 internal fragments, zero broken targets;
- 32 unique image references, all 32 assets used and decodable (`31 JPEG`,
  `1 PNG`), zero missing or unused assets;
- 51 rendered tables and 22 stat-block cards;
- 11 TOC groups and 11 credits items arranged in two columns;
- 10 full-width illustrations, 22 half-width illustrations, 21 explicit
  semantic-owner bindings and 12 real figure captions;
- zero escaped anchors/tables, technical comments, visible list-marker leaks
  or visual-only placeholders;
- related EN/RU/HTML regression: `118 passed, 6 skipped`.

The local `file://` restriction is handled by a temporary localhost server.
Browser QA proves the body duplicates are absent, the `2 + 1 + 5` narrative
references for Handouts 1-a/1-b/2 have working appendix targets, Handout 2 and
its Keeper note each occur once, all 32 images load, semantic-owner placement
is complete and `scrollWidth == clientWidth`. Desktop visual QA confirms that
one character portrait no longer wraps the next character's prose. A
narrow-screen single-column fallback exists in CSS but was not live-resized in
the browser session. The user accepted r6b on `2026-08-30`. The tested
`freeze_innsmouth_html_repo_input.py` gate promoted the exact accepted HTML and
all 32 assets to `inputs/innsmouth/html/accepted_20260830/`; its 7004-byte
manifest SHA-256 is
`12AA8FE9160F072E892562E5FFDCA00620A64B16009DC250F38F6C1DE981D661`.

## Historical direct PDF candidate — 2026-08-30

`scripts/build_innsmouth_pdf_from_accepted_html.py` re-verifies only the
permanent accepted HTML package, creates a deterministic print-only derivative,
prints it through Edge/Chromium and applies the generic production/print QA
before rendering every page through Poppler. The print derivative separates
cover, credits and source TOC at page boundaries without modifying accepted
HTML.

Current candidate:

`kb_creator/working/innsmouth_direct_pdf/accepted_20260830_candidate_r5/The_Innsmouth_Terror_RU.pdf`

- PDF: `10110361` bytes, SHA-256
  `2BA610AB1C8D163BBD36AC3CF855F5D16FAA49D592BDCDDC11D4E797A9EB47D4`;
- 52 A4 pages, one page size, 32 image XObjects and 88 internal links;
- zero empty pages, near-empty pages, half-empty pages, warnings or findings;
- production PDF report and print QA both pass;
- physical-page text gate proves credits-only page 2, TOC-only page 3 and body
  start on page 4;
- all 52 120-DPI page renders inspected in four contact sheets; cover, credits,
  TOC, low-text/image pages, stat blocks and handout tail also inspected at full
  size with no clipping or page-flow defect;
- expanded EN/RU/HTML/PDF regression: `129 passed, 6 skipped`.

Candidates r1-r4 are rejected diagnostic evidence: r1 orphaned the title from
the cover, r2 allowed credits/TOC overflow, and r3 mixed credits, TOC and body.
r4 remained defective for the same front-matter boundary class: Chromium ignored
the section-level CSS declarations, while the earlier visual review incorrectly
treated credits+TOC and TOC+body as separate pages. User screenshots invalidated
that false visual conclusion. r5 adds explicit print-only hard-break elements
and a fail-closed physical-page text gate. PDF is not yet a final release; user
acceptance and a fresh independent release verdict remain.

## Required evidence before user review

- all source lines/blocks accounted for in order;
- source-only `mineru-page` and `table-evidence` comments absent from RU;
- 154 heading positions and levels retained;
- 52 explicit anchors and 86 internal fragment destinations retained;
- 32 image paths retained in order;
- 51 HTML tables with 207 rows and 612 cells retained;
- stat blocks, handout identifiers and caption adjacency checked;
- no broken internal fragments;
- no accidental large English residue outside proper names, identifiers and
  user-approved terms.

Pre-cleanup mechanical evidence proved exact ordered parity for all 94 HTML
comments. Reader cleanup intentionally removed those 94 technical comments
from RU while leaving them in EN. The RU candidate still preserves 155 heading
levels, 50 anchor IDs, 117 total link destinations, 38 image paths, all 51
tables and 1,741 table/row/cell/`br` tags, 80 list prefixes and 62
strong-emphasis delimiters. It has 79 internal fragments and zero broken
fragments. All 33 visible cross-reference labels are Russian while their
destinations remain byte-identical. The
accepted EN's malformed `60% (307/12)` value is explicitly corrected in RU to
`60% (30/12)` and recorded in the glossary. Current final QA and critic closure
were bound to the pre-cleanup SHA-256
`B44CC2A82C8CB2C2763DDA4C97F0E67679DFB11CA87F8AAFA3D2244F3A546B20`.

## Git boundary

The accepted English pipeline and package entered `origin/main` at commit
`a7b2b21587a852cf7503f0d20d07f09a331c5b7a` on `2026-08-29`. The earlier
documentation/glossary/RU-reader-gate save-point was
`50c0e73329737f9eaa2516989be32e65ab73e808`. The ignored RU candidate entered
the permanent package only through the tested executable freeze/promotion
step; commit `bd0da472d63f58bc348e619e7393bcf6652a46e1` was pushed to
`origin/main`. The user explicitly authorized the final scoped save-point and
push on `2026-08-30`. The commit containing this context adds the r2 EN/RU/HTML/
PDF packages, all required pipeline scripts/tests and the portable next-PC
handoff to `origin/main`. Do not overwrite any accepted r2 package in place.

## MASTER_EN pipeline boundary audit — 2026-08-29

The first new-goal audit is recorded in
`MASTER_EN_PIPELINE_BOUNDARY_AUDIT_20260829.md`. It proves that Packet 5b is not
a clean `RECONSTRUCTED_EN`: the full MinerU reading candidate has 46 pages, 132
image links and 53 tables, while Packet 5b already has only 43 pages, 38 image
links and 51 tables. The old base producer also mixes source-backed corrections
with exclusion of pages `43..45`.

The accepted replacement architecture is intentionally small:
`source PDF -> MinerU reading extraction -> RECONSTRUCTED_EN -> MASTER_EN`.
The first implementation slice separates full-source reconstruction from page
and art suppression; it must not import the historical forest of one-off packet
scripts or mutate the accepted Packet 7 repository package.

## RECONSTRUCTED_EN Stage B candidate — 2026-08-29

`scripts/build_innsmouth_reconstructed_en.py` now consumes the identity-pinned
MinerU reading candidate, its 132 reading assets, the source PDF and the pinned
full-document OCR recovery assets. It retains all source pages `0..45`, ports
the accepted source-backed heading/semantic/paragraph/handout repairs, retains
all source artwork, and writes a deterministic page and asset inventory.

Generated candidate:

- external path:
  `RECONSTRUCTED_EN_package_r2_20260829/RECONSTRUCTED_EN.md`;
- Markdown: `138388` bytes, SHA-256
  `72CF965DF27C28D5D3927867E0A08C8655F5A7A117E108716FA84521649A8F13`;
- QA sidecar: `74886` bytes, SHA-256
  `D8103F92052F86945BABA9E964AE805C435C42AFA19C47E4BD8C59E998DEC106`;
- structure: `46` pages, `135` unique image links/assets, `53` tables,
  `169` headings, zero excluded pages and zero missing assets;
- asset inventory SHA-256:
  `421467CBDB51E96D6025EE733EB7E67CB61C6C6F15BA52C2F0DAE248801BE66A`;
- focused real-input tests: `13 passed in 3.68s`.

After removing only image links, technical comments and the publication-only
badge, normalized reader text on pages `1..42` is identical to Packet 5b.
Page `0` intentionally retains the source-visible standalone `THE` fragment
that the old reader-publication chain suppressed. The candidate has no TOC or
internal-reference projection. Stage B is implementation-ready but not yet
independently accepted; next work is the explicit Stage C projection.

The preceding `r1` generated directory is rejected: Stage C inventory review
proved that it retained the original failed Karen image crop `612c...` instead
of the source-backed clean crop `497d...`. The `r2` builder fixes the earliest
failing layer, pins the clean OCR asset hash, and proves exactly one clean and
zero old Karen references. `r1` must not be reviewed or promoted.

The first Stage C slice was implemented in
`scripts/build_innsmouth_master_en.py`. From the exact corrected Stage B hash it
applies only the approved scenario scope and 38-file reader-art allowlist,
suppresses the source cover duplicate and service badge, and produces a
navigation-free publication base: `126388` bytes, SHA-256
`6551D2E6367551EB71C41725996C6E52D7C6D7AE67119C0CF5C62502B5B11CE4`;
`43` pages, `38` images, `51` tables and `155` headings. Its normalized reader
content is exactly equal to Packet 5b.

Stage C is now implementation-complete locally. The same script applies the
accepted 34 leaf and 11 group TOC links, replaces only each printed `page N`
token while preserving outer punctuation, retains the visible Handout 1-b
number, inserts 50 explicit page-scoped stable anchors, removes technical
comments only after page-scoped projection, validates all 79 fragments, and
materializes the exact 38-asset package.

Corrected generated candidate:

- external path: `MASTER_EN_package_strict_pipeline_candidate_r2_20260829/`;
- Markdown: `130028` bytes, SHA-256
  `4A3DDE7AC0EA7A6815AE7FE3CAD38062CC828CF5880D549026E99D5496389A50`;
- QA sidecar: `14362` bytes, SHA-256
  `CED340C73D98B889269C915359FEDE44866CA04ED9216474C366BAE8284149CF`;
- asset inventory: `38` files, SHA-256
  `C1A9AB2F89650201C91FA74EAB809E16724D0C608534CFBFAA478AEEBA9CAE3A`;
- final structure: `51` tables, `155` headings, `50` unique anchors, `79`
  fragments, zero broken fragments, `33` ordinary `[link]` replacements,
  one Handout-number link, three intentionally literal external Keeper
  Rulebook page references and zero technical comments;
- all `765` nonblank reader lines equal the current user-accepted Packet 7
  successor;
- Stage C now pins the complete Stage B Markdown, QA and 135-asset inventory;
  its QA contains no device-specific absolute path;
- `freeze_innsmouth_master_en_repo_input.py` performs explicit-hash preflight,
  staged promotion, acceptance-manifest creation, post-copy verification and
  overwrite refusal; promotion has been tested only in a temporary directory;
- combined Stage B + C + freeze real-input evidence: `21 passed in 4.23s`.

This is the reproducible successor to the historical Packet 7 repository
package. The prior `r1` independent review in
`CRITIC_EN_PIPELINE_REVIEW_20260829.md` is invalidated by the Stage B
package-identity and freeze-gate changes.

Fresh `r2` independent review in
`CRITIC_EN_PIPELINE_R2_REVIEW_20260829.md` returned `REMEDIATION_REQUIRED` for
one P1: the freeze gate checked the caller-supplied QA hash but did not hard-bind
the QA's claimed Stage B provenance to the canonical Stage B Markdown, QA and
135-asset identities. The gate now performs that exact comparison, rejects
unexpected root directories and Windows absolute paths, and includes both
positive and tampered-provenance negative tests. Post-remediation evidence is
`23 passed in 4.12s`. Independent closure review appended to the same receipt
is `APPROVE`, with no remaining P0/P1/P2 findings and a canonical rerun at `23
passed in 4.14s`.

The user subsequently accepted `MASTER_EN r2` and authorized promotion, commit
and direct push to `origin/main`. The reviewed gate created and re-verified
`inputs/innsmouth/master_en/accepted_20260829/`: 41 files, 38 assets, total
`8085246` bytes, canonical repository inventory SHA-256
`A71F591B39D3DEB6C1EFE60AF48A22B5B779D0CABEDA4FB71FB1EB6F32F7E584`.
Both repository verifiers pass. The unified root-level EN release suite,
including historical Packet 7 compatibility, is `33 passed in 4.47s` with no
skips. A broad `kb_creator/tests` collection remains inapplicable in this
worktree because 15 archived page-proof/raw-authority tests reference modules
that are not present on this branch; no such module is in the EN commit scope.
Portable commands and the canonical authority are documented in
`inputs/innsmouth/master_en/README.md` and `PIPELINE.md`.

The remaining EN fidelity audit item is closed without changing the accepted
artifact: visual review of physical source-PDF page 40 (printed scenario page
36) confirms the publisher itself printed `Spot Hidden 60% (307/12)` for
Maggie. The accepted text correctly preserves this source-visible anomaly.
