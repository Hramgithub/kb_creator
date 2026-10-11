# Packet L — Dissociation run08 audit-v3 remediation architecture

## Receipt

- **Timestamp:** 2026-09-15T06:12:56+03:00.
- **Role / scoped override:** architecture and root-cause analysis, `gpt-5.6-sol` at `high`; read-only diagnosis except for this assigned handoff receipt.
- **Orchestrator policy owner:** main-chat `gpt-5.6-sol` at `medium`; orchestration ownership was not transferred.
- **Assignment state:** complete; bounded Packet L diagnosis and remediation specification.
- **Scope:** classify all 84 failures in the immutable run08 direct audit-v3 report, distinguish decision defects from consumer defects, define fail-closed geometry/equivalence/running-header remediation, and decide whether the sealed Stage01-04 replay prefix remains reusable.
- **Result:** **NO-GO for current Stage05; GO for bounded code remediation.** The 84 failures are 79 cross-view reader units that are already present in the selected Markdown, four exact reviewed running headers rejected only because MinerU typed them `text`, and one valid p3 OCR-equivalence row measured in incompatible crop coordinate systems. There is no narrative omission, unit-id drift, selected-coverage defect, interleaved-proof regression, or missing allowlist row. Decision-only remediation is insufficient and would weaken the ledger.
- **Files changed:** this receipt only.
- **Blocker:** Stage05 cannot pass until the v3 consumer uses canonical source-page geometry, admits uniquely proven exact split/merge subspans, and applies a narrow repeated-running-furniture guard. The existing failed report is historical evidence, not a passing Stage05 receipt.
- **Next action:** implement the three bounded consumer changes and tests below, obtain independent review, rerun the direct audit against the byte-identical run08 decisions/allowlist, then use the accepted downstream replay-resume route for Stage05/06. Do not invoke MinerU or recompute Stages01-04.
- **Elapsed time:** approximately 55 minutes including the prior checkpoint investigation and receipt recovery.
- **Token use:** exact role token count unavailable.

## Immutable authority and observed result

| Artifact / authority | Identity |
|---|---|
| run08 run identity | `D78CFBBC95AA51312C7339EAB3172D4CC8AA827801A42C23B3660104085E2F20` |
| replay bridge | `C61DFC69A9913ACB66817E98B2D5D4A510B75A1F182ADA52F94560127D69681B` |
| review queue | `D056BCA09236EA57D86BB4AD70788C0E7B99C9E04B582E35E337F934FEB01737` |
| comparison seal | `BEA28D6CC91B46D8EE5D80453A49C69E6BBD3EE6839409A96C26D3EECCCAF217` |
| geometry plan seal | `629F46F50F12EE20E74434B4423FA293191278FF98EF53C4A93A2C8D8A2BEEB0` |
| visual manifest | `5776D4E8917575A79C37768DEFA4E408C16DE433B15F25EA2B3831405CADA2EF` |
| decision set | `6F44BB66B3C9147BA753218FDFAC65DF15031E280BA986C2109A56A5B6F746F5` |
| reviewed allowlist v3 | 28,483 bytes; `DBEBC0B9713F5E260D290D03C89958A398A66DC27AE36531314D3D92908383B5` |
| direct audit v3 | 327,470 bytes; `98DE38C205949BB987D9AB5732BB5B6C6F95766E428B23239070FE25FD913C40`; `passed=false` |

The six run07/run08 merge packets and six page decisions are byte-identical. The direct audit resolved every exact authority and reviewed row: there are no stale-unit, authority, schema, selected mapping, ordered-proof-stream, assertion, or unused-allowlist errors. The allowlist contains 24 exact exclusions, two positional visual assertions and one OCR-equivalence class.

## Closed classification of all 84 errors

The ranges below enumerate every failing unit; there are no omitted members hidden by the grouping.

| Page | Exact error code / units | Count | Classification | Closed disposition after remediation |
|---:|---|---:|---|---|
| 1 | none | 0 | G1 cover-title assertion already succeeds | No action. |
| 2 | `unaccounted`: `original_pipeline_txt:8`, `original_pipeline_ocr:8` | 2 | Exact normalized whole-unit duplicates of one selected unit in another required view | Automatic `included_equivalent_exact`, only after unique same-page canonical geometry match. |
| 2 | `unaccounted`: `raster_pipeline_ocr:2-7,9-10,13-19` | 15 | Same as above | Same action; do not author exclusions. |
| 2 | `non_reader cannot discard body unit`: `raster_pipeline_ocr:1` | 1 | Exact reviewed top running header `DISSOCIATION`; extractor-type false positive | Existing exact `non_reader` row passes only through the repeated-running-furniture guard. |
| 3 | `unaccounted`: `raster_pipeline_ocr:24-33,38-41,43-44` | 16 | Exact normalized whole-unit duplicates of uniquely selected cross-view units | Automatic `included_equivalent_exact` after canonical geometry. |
| 3 | `non_reader cannot discard body unit`: `raster_pipeline_ocr:23` | 1 | Exact reviewed anthology running header `FEAR'S SHARP LITTLE NEEDLES` | Existing exact row passes through the repeated-running-furniture guard. |
| 3 | `OCR equivalence bounds failed page-003-examining-vessels-heading:raster_pipeline_ocr:37` | 1 | Valid reviewed OCR-equivalence row; false negative caused by crop/media coordinate mismatch | Keep the row byte-identical; recompute bounds in canonical source-page coordinates. |
| 4 | `unaccounted`: `raster_pipeline_ocr:49-56,59-64,66-67` | 16 | Exact normalized whole-unit duplicates of uniquely selected cross-view units | Automatic `included_equivalent_exact` after canonical geometry. |
| 4 | `non_reader cannot discard body unit`: `raster_pipeline_ocr:47` | 1 | Exact reviewed top running header `DISSOCIATION` | Existing exact row plus repeated-running-furniture guard. |
| 5 | `unaccounted`: `raster_pipeline_ocr:72-74,77-78` | 5 | Exact normalized whole-unit duplicates of uniquely selected cross-view units | Automatic `included_equivalent_exact` after canonical geometry. |
| 5 | `unaccounted`: `original_pipeline_txt:70`, `original_pipeline_ocr:70` | 2 | Exact strict subspans created by split/merged cross-view segmentation; both lie once inside selected `raster_pipeline_ocr:75` | Automatic `included_equivalent_exact_subspan` only with unique text occurrence, selected Markdown span and geometry containment. |
| 5 | `non_reader cannot discard body unit`: `raster_pipeline_ocr:70` | 1 | Exact reviewed anthology header with one-character OCR corruption, `FEAR'S SHARP LITTLE NFEDLES` | Existing exact row plus the bounded repeated-running-furniture cohort with p3. |
| 6 | `unaccounted`: `original_pipeline_txt:83`, `original_pipeline_ocr:83`, `raster_pipeline_ocr:81-88,90-95` | 16 | Exact normalized whole-unit duplicates of uniquely selected cross-view units | Automatic `included_equivalent_exact` after canonical geometry. |
| 6 | `unaccounted`: `raster_pipeline_ocr:96-102` | 7 | Exact strict subspans of one selected original-text statblock unit (`original_pipeline_txt:90`) | Automatic `included_equivalent_exact_subspan` only with unique occurrence and geometry containment; preserve canonical Markdown order. |

Closed arithmetic: `70` exact whole-unit equivalents + `9` exact split/merge subspans + `4` reviewed running headers + `1` reviewed OCR class = `84`. Page totals are p1 `0`, p2 `18`, p3 `18`, p4 `17`, p5 `8`, p6 `23`.

## Why v3 reports 79 unaccounted units after v2 reported 26

The numbers describe different populations. Packet G's v2 `26` were exact non-reader/visual/decorative/OCR units awaiting reviewed dispositions. Run08 v3 already has those dispositions: 24 remain exact exclusions, while the two p3 reader-heading OCR variants are represented by one equivalence class. The new `79` are alternate-view **reader** units.

V2 treated a unit as covered when its normalized text occurred anywhere in any selected anchor or in their concatenation (`audit_mineru_ai_merge_fidelity.py:321-325`). V3 correctly removed that permissive substring shortcut, but its replacement recognizes only exact-unit equality plus `_spatial_metrics`; `_fraction_bbox` currently validates that a geometry row exists and then divides MinerU coordinates by 1000 (`:395-407`). It never applies that row's MediaBox, CropBox, rotation or UserUnit. Thus equivalent text extracted from the cropped original layout and full-media raster layout is compared in incompatible frames and rejected.

Read-only matching of every reported unit against the selected normalized text establishes:

- `70/79` are exact whole-unit equality with exactly one selected cross-view unit;
- `9/79` are exact strict subspans caused by segmentation, each occurring inside exactly one selected source unit;
- after applying the canonical crop transform below, every one of the 70 has exactly one selected candidate at the existing `IoU >= 0.50` and `center_distance <= 0.035` bounds;
- every one of the nine subspans has exactly one selected candidate with smaller-box intersection coverage `>= 0.80`;
- unresolved or multiply resolved units: `0`.

This is not unit-id drift: exact allowlist units and all six byte-identical decisions resolve under fresh run08 authority. It is not selected coverage or interleaved-proof regression: the report has no mapping/proof-stream/assertion error, and both G1 assertions pass. It is not an allowlist-authoring gap: all rows are used, and adding 79 exclusions would incorrectly discard reader evidence.

## G2 geometry remediation

### Canonical coordinate contract

Replace `_fraction_bbox` with one shared, fail-closed transformation from each view's MinerU top-left `0..1000` crop-local bbox into top-left fractions of the source displayed MediaBox. For rotation `0`, with `u = bbox/1000`:

```text
x = (crop_x0 - media_x0 + u_x * crop_width) / media_width
y = (media_y1 - crop_y1 + u_y * crop_height) / media_height
```

For inherited rotation `90/180/270`, first map all four crop-local corners into PDF user space, multiply coordinates and boxes consistently by the positive `UserUnit`, apply the closed page-rotation affine transform around the MediaBox, then take the axis-aligned displayed bounding box and divide by the rotated displayed MediaBox dimensions. Use `Decimal` over the sealed geometry strings until the final reported metric. Reject rather than infer on a missing/duplicate view-page row, non-finite or reversed bbox, unsupported rotation, non-positive UserUnit, CropBox outside MediaBox, bbox outside the declared `0..1000` frame, or disagreement with `effective_displayed_size_points`.

All spatial consumers must use this one helper: OCR classes, automatic exact equivalence, exact-subspan equivalence, OCR-artifact correspondence and repeated-header classification. No consumer may compare raw normalized coordinates across views.

### Live p3 proof

The canonical selected unit has bbox `[478,93,865,119]` in an original view whose MediaBox is `[0,0,595,841]` and CropBox `[0,0,595,770]`. Its source-page normalized y interval is therefore `[0.169571938169, 0.193376932224]`. Raster alternate `[478,171,865,195]` uses CropBox equal to MediaBox and maps to `[0.171,0.195]`. The corrected metrics are `IoU = 0.880009352350` and normalized center distance `0.001078737218`, comfortably inside the unchanged v3 bounds. The report's `IoU=0` and `center_distance=0.054447` are artifacts of comparing crop-local y positions directly. The reviewed row is valid; threshold relaxation is forbidden.

## Exact split/merge equivalence contract

V3 needs one automatic disposition, not new decision rows:

1. alternate and canonical units are from different required views on the same source page;
2. the alternate normalized text is a non-empty exact substring of one selected canonical normalized unit, with exactly one occurrence;
3. that canonical unit has one existing selected source-to-Markdown mapping; derive and record the exact Markdown subspan, without changing Markdown or inserting another proof-stream item;
4. canonical source-page geometry gives smaller-box intersection coverage `>= 0.80` and a unique candidate; the alternate must not overlap a different selected reader unit;
5. the resulting disposition records canonical unit identity, selected mapping identity, normalized substring offsets, Markdown span, geometry metrics and policy version;
6. fail closed on fuzzy text, concatenation across multiple canonical units, ambiguity, zero-length/whole-unit misuse, reversed/overlapping Markdown spans, page/view equality, or missing geometry.

Whole-unit exact equality remains the preferred path and uses the unchanged OCR geometry bounds. Do not restore v2's unconstrained `unit in any anchor/joined anchors` rule.

## Safe repeated-running-header guard

`audit_mineru_ai_merge_fidelity.py:610-611` currently allows `non_reader` only for extractor types `page_number/header/footer`. MinerU typed four visually legitimate running headers as `text`; changing their exact unit identities or relabeling them `decorative` would be a decision bypass.

A generic `text` unit may pass an existing exact `non_reader` row only when the auditor derives a repeated-running-furniture cohort satisfying **all** of these predicates:

- every member is an exact reviewed exclusion with a non-empty rationale and exact run-local visual identity;
- same required view, distinct source pages, at least two reviewed members; an extractor-typed `header` may be a corroborating member;
- canonical source-page geometry places the whole bbox in the top margin (`y1 <= 0.06`) and peer boxes are co-located (`IoU >= 0.80`, center distance `<= 0.01`);
- normalized text is exact across peers or differs by at most one character with similarity `>= 0.92`; this bounded OCR tolerance applies only inside the already geometry-closed cohort;
- the text is absent from that page's rendered Markdown, and the unit has no selected/equivalent reader correspondence or spatial overlap with a body mapping;
- no member is selected, asserted, an OCR-equivalence alternate, or used by another disposition.

Run08 produces exactly two closed cohorts: p2/p4 plus the extractor-typed p6 `DISSOCIATION`, and p3/p5 `FEAR'S SHARP LITTLE NEEDLES/NFEDLES`. Repetition alone, top position alone, or reviewer classification alone is insufficient. No regex, page range, wildcard, book-specific string, reviewer-controlled threshold, or blanket `text -> non_reader` rule is allowed.

## Decision-only versus code remediation

| Failure set | Decision-only action | Required code action | Verdict |
|---|---|---|---|
| 70 exact cross-view reader duplicates | Adding exclusions/classes would create 70 manual suppressions and misstate reader content | Canonical geometry plus unique automatic `included_equivalent_exact` | Code only |
| 9 exact split/merge subspans | Excluding them or duplicating them in Markdown loses or duplicates proof | Unique, geometry-bound `included_equivalent_exact_subspan` disposition | Code only |
| 4 running headers | Existing exact rows and visual evidence are correct; relabeling `decorative` or editing `block_type` is forbidden | Derived repeated-running-furniture guard | Code plus byte-identical decision revalidation |
| p3 OCR equivalence | Existing row is correct; no threshold/row edit | Canonical geometry helper | Code plus byte-identical decision revalidation |
| G1 assertions / selected Markdown | No change | No change; current interleaved proof passes | Already closed |

No decision or allowlist edit is required. Any implementation that makes the current report pass by adding 79 exclusions, loosening global thresholds, accepting stale IDs, ignoring unused rows, or reverting to arbitrary substring containment is non-conforming.

## Regression and acceptance specification

1. **Crop normalization:** the live-shaped p3 pair above produces `IoU=0.880009352` and center distance `0.001078737`, while the old raw-frame result is asserted not to be used.
2. **Affine matrix:** synthetic CropBox offsets on all four sides, non-zero MediaBox origins, rotations `0/90/180/270`, and non-default valid UserUnit map the same physical rectangle identically across views. Missing, duplicate, outside, malformed, non-finite and unsupported geometry fails before disposition.
3. **Exact whole-unit equivalence:** same normalized text, one selected candidate and canonical geometry passes; wrong page, same view, two candidates, geometry miss and selected Markdown absence fail. Existing OCR bounds remain exact.
4. **Exact subspan positive cases:** p5 split units and p6 seven statblock segments map to unique canonical Markdown subspans with `>=0.80` smaller-box coverage and do not add duplicate proof-stream content.
5. **Exact subspan attacks:** repeated phrase, fuzzy edit, substring spanning two selected units, geometry collision, wrong-page match, partial Markdown occurrence and alternate mapped twice all fail closed.
6. **Running furniture positives:** the two run08 cohorts pass with the existing exact rows; p6 extractor-typed header can corroborate but does not exempt other predicates.
7. **Running furniture attacks:** a one-off top heading, repeated chapter title in body, bottom text, shifted peer, two-character corruption, matching selected body unit, absent visual identity, wildcard row, and same-page duplicate all fail.
8. **OCR class attacks:** the p3 class passes only after canonical transform; wrong crop, poisoned absolute coordinates, ambiguous counterpart, relaxed threshold, or old raw-frame metrics fail.
9. **Full run08 audit:** using byte-identical decisions and allowlist, pages p1-p6 have `unaccounted_unit_count=0`, complete ordered proof, no errors and global `passed=true`. A report with changed authority hashes is rejected.
10. **Replay boundary:** Stage01-04 payload and seal hashes remain unchanged; the accepted downstream adapter binds the new Stage05 consumer closure and new audit receipt, invokes no MinerU/provider, and allows Stage06 only after the fresh passing Stage05 result.

## Replay and closure consequence

Run08's sealed Stage01-04 prefix remains reusable: all 84 failures are downstream ledger semantics, and none changes a member of the accepted upstream producer closure. The failed audit SHA `98DE...13C40` does **not** remain reusable. After code and independent-review closure, rerun only the direct Stage05 audit and then the accepted HR3 downstream adapter. If that adapter requires a fresh run identity, it must replay/rebase the eligible run08 Stage01-04 authority through the accepted bridge; it must not mutate sealed source stages or copy paths manually. In either form, first revalidate the exact replay prefix and fail on any changed seal/hash. No full CPU/MinerU run is necessary.

This is not permission to resume now, materialize Stage06, infer acceptance, promote `RECONSTRUCTED_EN`, or proceed to publication.

## Files checked / evidence

- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`.
- `kb_creator/docs/plans/20260914-dissociation-publication/PLAN.md` and current project status.
- Packet G receipt `architect_dissociation_run_07_completeness_remediation_20260915.md`.
- Packet K receipt `engineer_dissociation_run08_allowlist_v3_audit_20260915.md`.
- Run08 `run.json`, Stage03 comparison/review packets, Stage04 `geometry_plan.json` and visual identities.
- Run08-decisions `decision_set.json`, all six page decisions, `reviewed_allowlist.v3.json`, and direct audit `source-visible-completeness-audit.v3.json`.
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`, especially v2 containment at lines 321-325; geometry at 395-418; OCR-class validation at 555-587; exclusion/body guard at 599-621; proof-stream closure at 625-650.
- Packet H authority-bridge and Packet I HR3/G1/G2 architecture/critic receipts for the stage-boundary constraint.

## Verdict

**Current Stage05: NO-GO. Bounded implementation packet: GO, subject to independent implementation review.** There are no true narrative omissions and no decision-authoring repair to make. Decision-only remediation is insufficient. Run08 remains an eligible immutable Stage01-04 replay source/prefix; after the downstream code correction, only Stage05/06 must be freshly produced under the accepted replay-resume authority. Final reconstruction and release acceptance remain pending their explicit gates and independent reviews.
