# Engineer receipt — Dissociation replay run-08 decisions and allowlist v3 audit

## Assignment and verdict

- Assigned/actual role: engineering, `gpt-5.6-sol`, reasoning `high` (user-scoped override).
- Result: **FAIL-CLOSED / NO-GO for replay resume**. Fresh replay, bridge, queue, page-decision, decision-set, allowlist schema, allowlist authority, and packet/comparison projection validation all pass. The direct production v3 content ledger rejects the semantically closed Packet G table with 84 errors; no bypass or extra exclusion was added.
- No acceptance was inferred or recorded. Stage05/Stage06, replay resume, materialization, promotion, MinerU, source execution, network, GPU, remote, and API paths were not invoked.

## Fresh authority

| Authority | Exact identity |
|---|---|
| run | `D78CFBBC95AA51312C7339EAB3172D4CC8AA827801A42C23B3660104085E2F20` |
| replay bridge seal | `C61DFC69A9913ACB66817E98B2D5D4A510B75A1F182ADA52F94560127D69681B` |
| review queue seal | `D056BCA09236EA57D86BB4AD70788C0E7B99C9E04B582E35E337F934FEB01737` |
| comparison seal | `BEA28D6CC91B46D8EE5D80453A49C69E6BBD3EE6839409A96C26D3EECCCAF217` |
| comparison semantic projection | `A3F184D86C3DD428F033949AB7DCF136ECC415331F14A969E8045A24DB360A81` |
| geometry plan seal | `629F46F50F12EE20E74434B4423FA293191278FF98EF53C4A93A2C8D8A2BEEB0` |
| visual manifest seal | `5776D4E8917575A79C37768DEFA4E408C16DE433B15F25EA2B3831405CADA2EF` |
| contract | `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E` |
| source | `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B` |

## Run-07 to run-08 comparison

- All six JSON merge packets are byte-identical. Page SHA-256 values remain: p1 `2E9D0D1CE5B75A02D6C4AE83BED04B3C68933620ED823B5C5F33B0A6D199CD94`; p2 `B6036691039492EC9653DB1E4A0587F77C0791A128C32E66084C929C8B4DEA7B`; p3 `162227C6D04730F775C63524E110713BBEF68BF05FA9A82856A5C8D8E4FFE5F0`; p4 `D65986B25A1DA40F12604BFFA6B55712D863AE6A3EC95483C8D9643A311DDB8D`; p5 `F5B4D3FE05A05B564AD89DD314F68BA29230506A51275AAEE2E37C5F779DBCA2`; p6 `32F6C966FC69D71E58DC856633FFB148EEC798F7EBF642A705BCC25A60D33753`.
- Review-queue item semantic projections are exact after removal of only the run-bound merge-packet authority object: both canonical projection hashes are `50EF53BF43A56D6C50F5C4C5A200857A8B8D12CE7FB21587EDC19CF538D01632`; ordered pages are 1–6 and all fresh states are `open`.
- The six corrected page decisions were copied byte-for-byte from run-07. Their SHA-256 values are p1 `147B2397D2DD594F0E4863AD6AB71E1F4A83DD7521124C78D47D129187A46E5C`; p2 `3E1CA05990CC2209DC1EC11BA5EC055E58C603020DD175816FB48D6499B8FEA6`; p3 `D18EC8A9671CE0D3D51705C79168828CE8CE389A822EBB3BE2B78AC9EFFCB5D8`; p4 `792E9638C5BF507FFD5AB5E9D4710A391B87E544D97ADEBB447AC62BDBA4E7CE`; p5 `56D243C1753A85CFD9E2B6A6DAB35ACB858D10863A132B2ABE090B1C5B79E85A`; p6 `8DB9CAEB866CA2C4D11FCB37884421E1D29FC6E9AD1C2C0C706EE201274801B6`.

## Draft decision/allowlist artifacts

- `decision_set.json`: 1,446 bytes, SHA-256 `6F44D4F236C4172F30CC21DD905C724ED9802DBC417A79F3A57F024C11AF46F5`; fresh queue/contract/source bound; `submitted_for_validation` is a validation state only, not acceptance.
- `reviewed_allowlist.v3.json`: 28,483 bytes, SHA-256 `DBEBC0B9713F5E260D290D03C89958A398A66DC27AE36531314D3D92908383B5`.
- Closed contents: 24 exact exclusions (2 `visual_only`, 20 `non_reader`, 2 `decorative`), two positional assertions, one OCR-equivalence class. Substitutions are empty. There are no p3 OCR-heading exclusions.
- G1 p1 cover title assertion uses `before_anchor` with selected `original_pipeline_txt:0`; G1 p2 drop-cap `T` uses `anchor_prefix` with selected `original_pipeline_txt:3`. Both are consumed without assertion error.
- G2 p3 class binds canonical `original_pipeline_txt:36` and exact alternates `original_pipeline_ocr:36` plus `raster_pipeline_ocr:37`, with fresh page-003 triptych evidence.

## Validation and direct v3 audit

Production functions invoked read-only against the fresh run: `validate_replayed_prefix()`, `validate_replay_review_queue()`, `validate_decision_set()`, `_validate_allowlist()`, Draft 2020-12 schema metaschema/instance validation, exact packet-to-comparison projection checks, and `audit_v3_content()`. The generated audit report was written only under the new decision root:

- `validation/source-visible-completeness-audit.v3.json`: 327,470 bytes, SHA-256 `98DE38C205949BB987D9AB5732BB5B6C6F95766E428B23239070FE25FD913C40`.
- Prefix/bridge/queue/decision/schema/authority/projection: **PASS**.
- Direct v3 content ledger: **FAIL**, 84 errors: 79 `unaccounted full source unit`, four `non_reader cannot discard body unit`, and one `OCR equivalence bounds failed`.

| Page | Errors | Unaccounted | Covered / required | Completeness | G1/G2 proofs |
|---:|---:|---:|---:|---:|---|
| 1 | 0 | 0 | 110 / 110 | 1.000000000 | 1 assertion |
| 2 | 18 | 17 | 10,290 / 12,925 | 0.796131528 | 1 assertion |
| 3 | 18 | 16 | 9,776 / 12,289 | 0.795508178 | 1 OCR class |
| 4 | 17 | 16 | 9,846 / 13,001 | 0.757326360 | — |
| 5 | 8 | 7 | 2,835 / 4,424 | 0.640822785 | — |
| 6 | 23 | 23 | 3,704 / 5,891 | 0.628755729 | — |

Exact unaccounted units are retained in the report. Compact closed listing: p2 `original_pipeline_txt:8`, `original_pipeline_ocr:8`, raster `2-7,9,10,13-19`; p3 raster `24-33,38-41,43,44`; p4 raster `49-56,59-64,66,67`; p5 `original_pipeline_txt:70`, `original_pipeline_ocr:70`, raster `72-74,77,78`; p6 `original_pipeline_txt:83`, `original_pipeline_ocr:83`, raster `81-88,90-102`.

The four exact non-reader guard failures are visually proven running headers typed by MinerU as generic `text`: p2 `raster_pipeline_ocr:1`, p3 `raster_pipeline_ocr:23`, p4 `raster_pipeline_ocr:47`, and p5 `raster_pipeline_ocr:70`. Relabeling them or adding blanket exclusions would violate Packet G.

The exact G2 failure is p3 `raster_pipeline_ocr:37`: lexical bounds pass (`token_levenshtein=1`, `string_levenshtein=1`, `similarity=0.981132075`) but current geometry reports `iou=0.0`, `center_distance=0.054447222`. The original OCR alternate passes (`iou=1.0`, `center_distance=0.0`, `similarity=0.962962963`). This demonstrates the auditor is comparing raw crop-shifted MinerU coordinates instead of the required crop/media-box-normalized page geometry.

## Blocker and next action

The current v3 consumer cannot represent the already reviewed, scenario-neutral evidence without weakening it: it lacks crop-aware geometry for raster/original equivalence, rejects visually proven running furniture solely because four MinerU blocks are typed `text`, and treats many complete cross-view split/segmented units as unaccounted. Per task instruction, engineering stopped fail-closed and did not edit pipeline code or add compensating rows. Independent architecture/critic review is required before a bounded consumer remediation; run-08 decisions remain unaccepted and must not be resumed.

## Changed files

- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/decision_set.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/reviewed_allowlist.v3.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/pages/page-001.json` through `page-006.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/validation/source-visible-completeness-audit.v3.json`
- this receipt
