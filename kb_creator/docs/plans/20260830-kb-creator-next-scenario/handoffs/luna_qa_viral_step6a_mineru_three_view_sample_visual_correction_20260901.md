# Luna visual QA correction receipt — Viral Step 6A three-view sample

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-mineru-three-view-sample-visual-correction`
- Role: execution-only visual QA (`gpt-5.6-luna`, high)
- Orchestrator policy owner: main-chat `gpt-5.6-sol` / medium
- Assignment state: `matched` (platform runtime model/effort not independently verifiable)
- Scoped override: `none`
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Timestamp: `2026-09-01T13:46:45+03:00` (Europe/Moscow)
- Elapsed time: approximately 6 minutes; exact platform elapsed time unavailable
- Token use: unavailable to this contributor
- Result: `PASS`

## Scope and immutable predecessor

Read-only visual correction of the already rendered files under:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_sample/evidence/rendered`

The immutable first receipt was checked by its declared SHA-256:

`luna_qa_viral_step6a_mineru_three_view_sample_execution_20260901.md`

`4425D6469E172BA992BD48A8409348D9271102AB253DA7B3C646840BED6C903E`

No marker, preparation, MinerU, comparator, focused-test or `pdftoppm`
command was rerun. No sample-root, source, code, test, plan/context,
production, Git or predecessor file was written. This receipt is the only new
write authorized by the correction packet.

## Deterministic file validation

Exactly eight PNGs were present in each view. Every file opened successfully
at high detail, and every image had pixel dimensions `1275 x 1650`, mode RGB.

| View | File | Bytes | SHA-256 | Dimensions |
|---|---|---:|---|---|
| original_hybrid | `page-1.png` | 1,973,304 | `4E368D53437EF4B09C8C77BF392262CB473D76128E5B0161F526B929188A9FAA` | 1275x1650 |
| original_hybrid | `page-2.png` | 2,348,999 | `1EAD4A5594174D4E7DBC71362994F6FF2F772914C5DB4BA0BBCF1DD652D8C305` | 1275x1650 |
| original_hybrid | `page-3.png` | 1,116,344 | `7291D2C7F4BE1D2A6E9E5C19CE614F5EC7ED6127D6AD6D71992806CF96351DB4` | 1275x1650 |
| original_hybrid | `page-4.png` | 2,075,965 | `3B60AFB61BF15DF8F0BE2FA773C0ECC74FF5F2CEC3168F7C68B4A4F213202D98` | 1275x1650 |
| original_hybrid | `page-5.png` | 1,710,736 | `ACFB07D3691F706785FA1483A5ADF23E0883419252817A066F6F6C850FFBCE57` | 1275x1650 |
| original_hybrid | `page-6.png` | 1,446,391 | `41CB1E16B7FB9B60FE9F035888534DF543F0A39B0A06A976F43ED6E760924B54` | 1275x1650 |
| original_hybrid | `page-7.png` | 2,217,442 | `DA222A0E5467F86C602803854343684ED0F6CB01E49EAD43A66A2163E87B8728` | 1275x1650 |
| original_hybrid | `page-8.png` | 1,167,586 | `CC42FFE7E9DBD3ADBADDDB2E49DECF91C8295101A55E3BF217590D04A7FD1C43` | 1275x1650 |
| original_pipeline_ocr | `page-1.png` | 1,947,782 | `05F1B59C8A3EDDBC26B7F028AD722016604AC305CA4AD2E6F913EB7B8B75869C` | 1275x1650 |
| original_pipeline_ocr | `page-2.png` | 2,345,667 | `D181722E0E244057555E57D1E1A318954D29C5AE8028FE0807826E1577B54359` | 1275x1650 |
| original_pipeline_ocr | `page-3.png` | 1,224,855 | `B62752376CE73CAA5759274EF2C2E2731C10688287B79D83EAE7FCB135FBEBDE` | 1275x1650 |
| original_pipeline_ocr | `page-4.png` | 2,076,322 | `4C323CA4B6A0C606430D05AAEAEDC30E99208ACF76E90ACCA50E231D9F9A912A` | 1275x1650 |
| original_pipeline_ocr | `page-5.png` | 1,711,192 | `40AE31713904FD6EF40FECE2E863A3238158F5C94DCE2DDC8EF0954772DDED29` | 1275x1650 |
| original_pipeline_ocr | `page-6.png` | 1,378,361 | `56366EF74D536F706B61533A455EE361A7D0C4AA41D2FCFB93C0C127AA21187D` | 1275x1650 |
| original_pipeline_ocr | `page-7.png` | 2,163,462 | `058553D6EEEFFD40AD24F44D7762551B83D41AA3F5D782B7AD823EF4F1DD6224` | 1275x1650 |
| original_pipeline_ocr | `page-8.png` | 1,173,901 | `36CECEAA18162793DF50EA7C298C7F6C8F903BF9D75295544EADF20DB7BBF3E7` | 1275x1650 |
| raster_hybrid | `page-1.png` | 2,224,336 | `E68A0140652E89C4B39587E91306B7197818CAE6D446AA18913B655AE6776104` | 1275x1650 |
| raster_hybrid | `page-2.png` | 2,504,497 | `0363F10604862594060A3857C77A4731A44CAE2184DC225B58D9F2895A0FFB00` | 1275x1650 |
| raster_hybrid | `page-3.png` | 1,176,203 | `C828B6F27FCAE76355CC84B7F6071A9CCAF7794F1784513666118932E16AF199` | 1275x1650 |
| raster_hybrid | `page-4.png` | 2,117,584 | `F947F41C74888FAA11BA8C86D34E78776DF487CD6432BC3A8BC648BD6E6FE273` | 1275x1650 |
| raster_hybrid | `page-5.png` | 1,731,348 | `6394C2C69942EFCCB6C9DC5525008A505901D832D450999C17FB9010AF96D86C` | 1275x1650 |
| raster_hybrid | `page-6.png` | 1,436,759 | `9DF92C0D30C251A9BCD9BC1810AF944BCB87BFBB90824BD1D1BAA11FF21ECAEC` | 1275x1650 |
| raster_hybrid | `page-7.png` | 2,268,379 | `48D51EF964BD86F62035B0319486165B77FBCDA31E2E3DA1CA5CC4041D1C1AAD` | 1275x1650 |
| raster_hybrid | `page-8.png` | 1,208,954 | `679B2D6769DE81CAC0A4DA8D1BFB108A1EC60A685541EBC13E3BB37DF9603817` | 1275x1650 |

## Page-by-page visual QA and cross-view comparison

Rendered page numbers map to source PDF pages in the required order:
`1→5`, `2→12`, `3→53`, `4→69`, `5→104`, `6→109`, `7→115`, `8→123`.
All 24 pages were actually opened and inspected at high detail.

| Rendered page → source page | original_hybrid | original_pipeline_ocr | raster_hybrid | Cross-view result |
|---|---|---|---|---|
| 1 → 5 | Contents page visible; headings, lists and table regions boxed; no clipping or overlap defect | Full two-column contents regions visible; text legible; no clipping | Fine-grained heading/list regions visible; no clipping | Segmentation granularity differs (expected signal); same visible page |
| 2 → 12 | Two-column prose and callouts fully visible; text readable to page boundary | Same prose/callout content visible and readable | Same content visible; boxes follow prose blocks | Views agree on visible content; ordinary box-boundary differences only |
| 3 → 53 | Full-page aircraft art visible; no colored layout box rendered | Aircraft art visible; central image region boxed | Full-page aircraft art visible; no colored layout box rendered | Hybrid/raster omit a visible overlay box while pipeline boxes central art; extraction difference, not image clipping |
| 4 → 69 | Player Handouts title, map image and Handout #1 visible; regions aligned | Same title/map/handout visible; no clipping | Same title/map/handout visible; no clipping | All three preserve page composition; box segmentation/color differs |
| 5 → 104 | Keeper Maps title and large labeled map visible; note text legible | Same map and note visible; boundaries aligned | Same map and note visible; no clipping | Same visible page and map; ordinary overlay differences |
| 6 → 109 | Composite page visible; administrator/attic maps, photo and hospital map boxed separately | Full composite visible, but mostly one large merged image region; text/art legible | Composite submaps/photo/hospital map boxed separately | Pipeline merging versus hybrid granular regions is an extraction signal; no visual clipping |
| 7 → 115 | Investigator sheet, portrait, characteristics, skills, weapons and combat areas visible; text readable | Same sheet and all major regions visible; no clipping | Same sheet and all major regions visible; no clipping | Box granularity differs; all substantive visible regions retained |
| 8 → 123 | Product images, labels/prices, slogans and QR code visible; no clipping | Same products, labels/prices, slogans and QR code visible | Same products, labels/prices, slogans and QR code visible | All three preserve page composition; ordinary grouping differences only |

No page showed unreadability, page-boundary clipping, overlay-induced overlap,
or a missing visible page image. The page-53 and page-109 box differences are
recorded for later merge/reconciliation and are not automatically classified as
defects.

## Result and next action

PASS is limited to this visual correction gate: all 24 existing PNGs were
readable and actually inspected, and all required per-view/source-page findings
were recorded. It does not decide merged truth, full-document extraction,
production readiness or release.

Next action: the orchestrator may bind this receipt as the completed visual QA
evidence and continue with the separately authorized next gate. No repair or
rerun is requested by this receipt.

This is a single-write detached handoff receipt; compute its SHA-256 only after
the final write.
