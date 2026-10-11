# Innsmouth: source reconstruction -> MASTER_EN -> MASTER_RU -> HTML -> PDF

Goal ID: `20260826-innsmouth-direct-master-ru-publication`

State: `PUBLICATION COMPLETE; FORMAL INDEPENDENT RELEASE VERDICT PENDING`

## Objective

Finish the publication through one reproducible, ordered chain in which source
reconstruction, reader/editorial preparation, translation and rendering remain
separate:

`source PDF -> RECONSTRUCTED_EN -> MASTER_EN -> MASTER_RU -> HTML -> PDF`

## Authoritative input

The immutable source PDF and its pinned MinerU Hybrid/high extraction supply
source prose, structure and artwork. The promoted strict-pipeline English
package below is the sole production authority for translation:

`kb_creator/inputs/innsmouth/master_en/accepted_20260830_r2/MASTER_EN.md`

- bytes: `127769`;
- SHA-256: `31F67A2865BF00A48F197333A162AD56AA0F56061068D3BFD6B564591F9AA3C2`;
- strict successor promoted through the gate on `2026-08-30`; the complete
  portable publication chain is included in the final scoped release commit.

`packet7_user_review_20260826/` remains immutable historical comparison
evidence, not the production translation input.

Historical RU v6, old cleaned EN, the historical `unit_id/source_hash` bridge,
legacy translation memory and the poisoned Packet 7 test directory are not
translation sources and must not be opened for prose reuse.

## Completed — separate EN reconstruction from the editorial master

User-review finding recorded on `2026-08-28`: the completed English chain
mixed two different stages—faithful source reconstruction and editorial/
publication preparation before translation. The strict replacement now records
and verifies those stages separately.

- [x] Define and independently verify `RECONSTRUCTED_EN`: faithful source text,
  order, columns, headings, tables, stat blocks, handouts, illustrations and
  captions, without newly authored navigation or reader-output suppression.
  Corrected implementation candidate built on `2026-08-29` at
  `RECONSTRUCTED_EN_package_r2_20260829/`: `138388` bytes, SHA-256
  `72CF965DF27C28D5D3927867E0A08C8655F5A7A117E108716FA84521649A8F13`;
  `46` pages, `135` image links/assets, `53` tables and `169` headings.
  Focused real-input evidence: `13 passed`; independent verification remains
  open, so this checkbox is intentionally not closed yet.
- [x] Audit Packet 5b (SHA-256
  `751DE433161C2EA3AD174C8B20E7803130F2462C02DA267E863A2A9EA0004D2F`) as
  the closest preserved reconstruction candidate; do not accept it
  automatically because reconstruction and publication operations had already
  begun to interleave. Result:
  `MASTER_EN_PIPELINE_BOUNDARY_AUDIT_20260829.md`; Packet 5b is not admissible
  as `RECONSTRUCTED_EN` because pages `43..45` and 86 scenario image references
  were already suppressed.
- [x] Derive a separately reviewable `MASTER_EN` from accepted
  `RECONSTRUCTED_EN` using only explicit editorial operations: page-reference
  links, TOC/navigation anchors, handout links, duplicate-handout suppression
  in body, and the approved reader-art publication policy. The handout policy
  now suppresses the exact body duplicates of Handouts 1-a and 2, relocates the
  Handout 2 Keeper note to the appendix, and links all eight narrative mentions
  to their appendix targets. It also consolidates Handout 2 to one text block
  and excludes its three seals and two signature crops from reader assets while
  retaining them in reconstruction evidence. Stage C implementation is complete locally:
  candidate Markdown `127967` bytes, SHA-256
  `DFDF2C0DAA1B5B642C217B4B5C52732070F4CC66582D40A98A77C0E48F2AE405`;
  `32` assets, `51` tables, `154` headings, `52` anchors, `86` resolved
  fragments and zero technical comments. Corrected `r2` also pins the full Stage B
  QA/135-asset package without device-specific paths. The reproducible
  freeze/promote gate has passed a temporary promotion/verify rehearsal.
  Initial `r2` review found a P1 provenance-binding gap in the freeze gate. The
  gate now hard-compares canonical Stage B Markdown/QA/135-asset identities and
  has a tampered-provenance negative test. Post-remediation evidence is `23
  passed`; independent closure review is `APPROVE` with no remaining P0/P1/P2
  findings. The user explicitly accepted `r2`; the reviewed staged gate
  promoted it to `inputs/innsmouth/master_en/accepted_20260829/` with a
  deterministic acceptance manifest. The `2026-08-30` successor removes the
  one remaining decorative letter-seal crop at this same Stage C boundary and
  has been promoted locally to `accepted_20260830_r2/` through the same gate.
- [x] Correct EN fidelity defects at the reconstruction layer rather than only
  in RU; specifically recheck the accepted EN `60% (307/12)` stat value against
  the source. Visual review of physical PDF page 40 (printed scenario page 36)
  confirms that the source itself prints `Spot Hidden 60% (307/12)`; preserve
  it as an explicit source-visible publisher anomaly.
- [x] Record that the current main checkpoint verifies the accepted final
  package and its last successor, but is not yet a complete executable
  `PDF -> RECONSTRUCTED_EN -> MASTER_EN` pipeline; close that reproducibility
  gap before calling the English pipeline complete. The separated Stage B,
  Stage C and freeze/promote scripts, tests and portable commands now form that
  executable chain.
- [x] Keep the current `MASTER_RU` as the accepted direct translation draft.
  After the revised `MASTER_EN` was accepted, the bounded repository gate
  applied only the separately approved Hobby World terminology sync; the whole
  document was not retranslated.
- [x] Do not start HTML/PDF or finalize MASTER_RU acceptance until this English
  boundary decision is resolved and the resulting MASTER_EN is user accepted.

## TODO — reproducible MASTER_RU repository acceptance

Recorded on `2026-08-29`: the user completed the full reading review of the
current `MASTER_RU` candidate and reported no remaining reader-text defects.
Moving that candidate from ignored `working/` into a permanent repository input
must be an executable pipeline step, not a manual copy operation.

- [x] Implement one bounded `freeze/promote MASTER_RU` entrypoint. Its explicit
  inputs are the accepted `MASTER_RU.md`, the selected 32 RU reader assets from
  the 33-asset canonical accepted MASTER_EN package, the canonical skill glossary, and the permanent
  target directory.
- [x] Before writing the target, reject `mineru-page` and `table-evidence`,
  verify the accepted MASTER_RU identity, exactly 32 ordered image references,
  all 32 asset files and hashes, all 51 tables, and zero broken internal links.
- [x] Check the accepted RU skill labels against
  `docs/terminology/CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md`.
- [x] Create the permanent package at
  `inputs/innsmouth/master_ru/accepted_20260830_r2/` through that entrypoint only.
  The package contains `MASTER_RU.md`, sibling `assets/`, and
  `MASTER_RU.acceptance.json` recording the MASTER_EN origin, RU identity,
  glossary path/hash, asset inventory, and validation results.
- [x] Provide a repeatable verify mode for the frozen package and add focused
  tests for successful promotion plus rejection of technical comments, missing
  or changed assets, broken fragments, wrong table/image counts, terminology
  drift, and accidental overwrite.
- [x] Run the promotion and verification commands and update status/context
  with exact identities. Manual copying from `working/` is prohibited.

## TODO — final publication chain after all preceding TODOs

Do not start this item until every preceding TODO in this plan is closed. The
downstream production chain is:

`accepted MASTER_RU -> HTML -> user acceptance of HTML -> PDF -> final acceptance`

- [x] Apply the approved Hobby World skill glossary to the accepted RU text as
  one bounded terminology synchronization, without retranslating or otherwise
  re-editing accepted prose.
- [x] Correct the stale TOC assertion so it checks the current structured
  `{title, level, href}` entries, including the current final Handout 2 child,
  without changing production code. The focused promotion regression suite
  passes `12 passed, 1 skipped`; the unified EN/RU/Keeper command passes
  `72 passed, 14 skipped`.
- [x] Use only the tested `freeze/promote MASTER_RU` pipeline step defined above
  to create and verify the permanent tracked RU package with its 32 assets and
  acceptance manifest.
- [x] Close independent review P1: `--verify` now pins the exact acceptance
  manifest (`3393` bytes / SHA-256
  `D1548C72B8DC7F0A713B1C36807F018F88434FF7CBDF59E51254A4DA64A7613F`),
  and rejects metadata-only manifest mutation plus missing, changed, or extra
  assets. Focused remediation tests pass `6/6`; fresh closure review is required
  before commit authorization.
- [x] Commit the authorized RU save-point and push it directly to
  `origin/main`: commit
  `bd0da472d63f58bc348e619e7393bcf6652a46e1`; post-push frozen-package
  verification passes.
- [x] Fix the semantic-anchor defect class at its earliest layer. The
  `MASTER_EN` pipeline now binds 16 affected `nri-h-*` IDs to their existing
  headings and rejects heading-class anchors placed inside prose; the sole
  documented body exception is `The Innsmouth Terror`. The RU promotion gate
  reproduces the same 16 anchor moves at the corresponding Russian headings.
  Anchorless EN and RU comparisons are byte-identical to their accepted
  predecessors, so no reader prose or links changed. The later seal-removal
  successor changes only the one approved decorative asset reference.
- [x] Build one fresh self-contained HTML successor strictly from the frozen
  accepted `MASTER_RU`, without a historical v6 input, intermediate
  `KeeperBook`, duplicate generated TOC, or manual HTML edit. Historical r6b:
  `225985` bytes, SHA-256
  `375A98E69FD763C85465A9E1D64D45885D475AFFDFCBBB5AC9862FD36ED4BEAA`.
  The later PDF review superseded it. Current r7f is `223459` bytes, SHA-256
  `040C7AF42A76241B3BC280350C0151096CF81E5F9A9194E6F5003B0388E4EF39`.
- [x] Obtain user visual acceptance of r7f after verifying its TOC and internal
  links, all images, tables, stat blocks,
  characters and monsters, handouts, absence of technical comments, visual
  layout and print breaks. Mechanical and positive-content QA currently prove:
  52 anchors, 86 resolved fragments, 32/32 decodable and used assets, 51
  tables, 22 stat-block cards, zero escaped structural markup and zero
  technical comments. Historical r6b remains frozen under
  `inputs/innsmouth/html/accepted_20260830/`, but it is not the input to the
  successor release. Localhost browser QA confirms the body duplicates are
  absent, all
  `2 + 1 + 5` Handout 1-a/1-b/2 references link to existing appendix targets,
  all 32 images load, 11 images remain full-width, 21 are right-floated with
  semantic-owner wrapping, and the TOC uses two columns. r7f has a source-art
  title page and no content-warning or credits block. The user accepted r7f on
  `2026-08-30`; the gate promoted it to
  `inputs/innsmouth/html/accepted_20260830_r2/` with manifest SHA-256
  `B0ADDD901CCD0DED10D84D331B3F168987070558641D374F13ABC30852E6D7E6`.
- [x] After r7f HTML acceptance, promote it through the tested freeze gate and
  build the final PDF through the same recorded route; then
  verify clipping, page flow, tables, stat blocks, illustrations, captions,
  links and handouts. Historical r5 is 52 A4 pages, `10110361` bytes, SHA-256
  `2BA610AB1C8D163BBD36AC3CF855F5D16FAA49D592BDCDDC11D4E797A9EB47D4`.
  Structural QA and print QA have zero findings; all 52 Poppler renders were
  inspected through contact sheets and risk pages at full size. A new
  physical-page gate proves page 2 contains credits but no TOC, page 3 contains
  the complete TOC but no body start, and page 4 contains the body start. The
  expanded historical EN/RU/HTML/PDF regression was `129 passed, 6 skipped`.
  The final r6 PDF has 46 A4 pages, 32 image XObjects, 88 internal links,
  97421 text characters and no structural findings. It is `11566429` bytes,
  SHA-256
  `8D79F72CB61626B05DE7EC000E140FA0C893C6B3D2DC693A64DF45AF756AE202`,
  and is frozen at `inputs/innsmouth/pdf/accepted_20260830_r2/`. All 46 final
  renders are pixel-identical to the user-accepted r7f preview set. The user
  directed the project to treat successful PDF QA as acceptance. A fresh
  independent release verdict remains pending under repository governance.
- [x] Implement the user-approved duplicate-handout suppression at the
  `MASTER_EN` editorial layer and project it deterministically into MASTER_RU;
  do not edit generated HTML by hand.

## Direct work plan

1. **Accepted MASTER_EN in main — completed.**
2. **Fresh direct translation — first complete draft produced.**
   Translate the accepted file from start to finish into one new
   `MASTER_RU.md`. Preserve Markdown/HTML structure while translating visible
   prose and labels. Do not introduce an intermediate alignment platform.
3. **Mechanical structure check — completed for the current candidate.**
   Compare source and RU order, headings, anchors, link destinations, image
   paths, HTML table topology, stat-block and handout boundaries. Source-only
   reconstruction comments (`mineru-page`, `table-evidence`) are excluded from
   reader-facing RU and blocked by the RU-to-Keeper entrypoint. Check that no
   source section or visible paragraph disappeared.
4. **Independent editorial QA — completed and critic-approved for user review.**
   Review Russian completeness, meaning, terminology, names, untranslated prose
   and Markdown damage; correct the candidate and rerun structure checks.
5. **User reading acceptance and repository promotion of MASTER_RU — completed.**
   The user accepted the candidate's reader text and structure on `2026-08-29`.
   The executable freeze/promotion gate created the permanent package, and the
   authorized save-point was pushed to `origin/main`.
6. **HTML from accepted MASTER_RU — completed.**
   r7f was accepted and promoted to the permanent r2 HTML package. r6b remains
   historical evidence only.
7. **PDF from accepted HTML route — completed.**
   The direct builder re-verified accepted HTML, rendered 46 A4 pages, passed
   structural/print QA and explicit physical front-matter gates. All 46 final
   page renders match the accepted r7f preview set. The exact PDF and manifest
   are frozen in the permanent r2 PDF package.
8. **Portable publication save-point — completed; formal release verdict pending.**
   Exact input/output identities, QA evidence, scripts, tests and a next-PC
   handoff are included in the scoped commit and pushed to `origin/main` under
   explicit user authorization. Repository governance still requires a fresh
   independent `gpt-5.5` verdict before labeling this a formally approved
   release.

## Translation rules

- Preserve anchors, link destinations and asset paths exactly. Preserve only
  comments admitted by the target-layer contract; source reconstruction
  comments are excluded from reader-facing RU.
- Preserve heading levels, table tags/shape, list markers, emphasis, stat-block
  order, handout numbers, illustrations and caption attachment.
- Translate from current English meaning, not by importing old Russian prose.
- Keep proper names and game identifiers consistent through one small glossary;
  resolve uncertain terms during editorial QA rather than blocking the draft.
- Temporary draft roughness is allowed; missing content or structural mutation
  is not.

## Current boundary

The earlier uncommitted translation-unit/compiler experiment was rejected as
unnecessary and removed on `2026-08-27`. It produced no real Russian master,
HTML or PDF and did not enter Git.

The first complete direct candidate now exists at
`kb_creator/working/innsmouth_direct_master_ru/MASTER_RU.md`. It is retained as
the exact accepted promotion source. The first independent QA returned
`REMEDIATION_REQUIRED`; the listed
English common terms, visible link labels, terminology/grammar defects and the
source stat typo were corrected in the single candidate. A second QA then found
one Handout 2 tail-order defect; it was corrected. Final QA then found and
closed one remaining `Boston` residue. Exact ordered EN/RU blank and structure
parity passed before reader cleanup; final QA verdict was `PASS`, and a fresh
independent `gpt-5.5` critic verdict was `APPROVE_FOR_USER_REVIEW`. During user
review, all source-only `mineru-page` and `table-evidence` comments were removed
from RU without removing tables or content anchors. The user completed reading
review and accepted its reader text and structure on `2026-08-29`; repository
freeze/promotion then completed through the tested gate. The user-reported
missing sibling assets directory had been
restored with all 38 canonical files and byte/hash verified; the requested
character-count audit also closed the complete skill-check case-agreement
class. The subsequent approved handout projection and seal-crop correction now
leave 32 canonical assets. The user later accepted r7f HTML, which is frozen as
the canonical r2 HTML package. Final PDF r6 was built only from that package,
passed structural and visual QA, and is frozen as the canonical r2 PDF package.
The publication chain is portable and complete; only the formal independent
release verdict remains pending.
