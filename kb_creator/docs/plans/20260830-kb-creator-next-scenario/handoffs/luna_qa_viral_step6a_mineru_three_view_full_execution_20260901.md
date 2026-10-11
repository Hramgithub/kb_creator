# Luna QA receipt — Viral Step 6A full three-view MinerU execution

- Goal id: `20260830-kb-creator-next-scenario`
- Step: `viral-step6a-full-three-view-mineru-execution`
- Role: bounded QA / execution-only (`gpt-5.6-luna`, policy effort `high`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: none
- Timestamp: `2026-09-01 14:22:13 +03:00`
- Elapsed time: approximately `24m25s` from fresh-root creation through acceptance evidence
- Token use: unavailable

## Scope and result

`PASS` for the supplied accepted specification and file scope. One fresh full
root was created and the exact raster-only preparation plus all three exact
profiles were executed once, sequentially. Comparator, focused tests, output
contracts, inventories, and PDF page counts passed. No visual rendering or
visual inspection was performed.

Allowed writes observed:

- fresh root: `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full`
- this single receipt;
- normal MinerU runtime cache/temp/config activity.

No code, tests, source/sample/prior roots, plans/context/config, verifier,
MASTER, production, or Git files were edited.

## Commands and native results

All frozen commands were run from `D:\NRI\.worktrees\kb-creator-viral`.

| Operation | Native exit | Elapsed evidence | Raw console |
|---|---:|---:|---|
| PDF operation marker, exact packet command, once | 0 | command completed before preparer | not emitted by marker |
| raster-only preparer, exact Terra command | 0 | approximately 5m13s | `prepare_raster_only.console.txt` |
| `original_hybrid` / `hybrid_high`, retained source | 0 | 283.452s (`14:03:05.692`–`14:07:49.144`) | `original_hybrid.console.txt` |
| `original_pipeline_ocr` / `pipeline_ocr`, retained source | 0 | 275.901s (`14:08:14.550`–`14:12:50.451`) | `original_pipeline_ocr.console.txt` |
| `raster_hybrid` / `hybrid_high`, raster-only PDF | 0 | 307.011s (`14:13:13.696`–`14:18:20.707`) | `raster_hybrid.console.txt` |
| three-view comparator | 0 | 2.880s | `compare.console.txt` |
| focused test file | 0 | 2.375s | `terra_focused_tests.console.txt` |

The three MinerU consoles each contain `Processed 124/124 pages`.

## Verification and evidence

Source identity rechecked read-only: `20,718,150` bytes,
SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.

Preparation output:

- manifest mode: `raster_only`;
- ordered mappings: `124`, exact `sample_page`/`source_page` values `1..124`;
- input PDFs: exactly `1` (`viral_full_raster.pdf`);
- manifest outputs keys: exactly `raster_pdf`;
- raster PDF: `776,631,598` bytes,
  SHA-256 `E9F2E340147154BEA9668FCFEE99BFC3AAB8FF8430296F1D9C51511FBFD9B238`;
- `viral_full_vector.pdf`: absent (recursive count `0`);
- manifest records raster pages as text-free and Letter 612x792 points.

Profile contract results:

| Profile | Files | Bytes | Page coverage | Required artifacts | Asset references | Missing assets | PDF pages |
|---|---:|---:|---|---|---:|---:|---:|
| `original_hybrid` | 211 | 64,141,255 | exact 124, `page_idx` 0..123 | Markdown, v1/v2 content lists, middle JSON, layout PDF, origin PDF | 190 unique | 0 | 124 |
| `original_pipeline_ocr` | 112 | 92,870,143 | exact 124, `page_idx` 0..123 | Markdown, v1/v2 content lists, middle JSON, layout PDF, origin PDF, span PDF | 104 unique | 0 | 124 |
| `raster_hybrid` | 199 | 1,574,869,863 | exact 124, `page_idx` 0..123 | Markdown, v1/v2 content lists, middle JSON, layout PDF, origin PDF | 178 unique | 0 | 124 |

`pdfinfo` native exit was `0` for each layout PDF; all reported `Pages: 124`
and Letter page size. Comparator output is `status: pass` and `failures: []`.
Focused test console reports `11 passed in 1.80s`.

Recursive inventory evidence uses sorted canonical lines
`relative-path|bytes|file-sha256` with UTF-8 LF and a SHA-256 over the complete
section stream:

| Section | Files | Bytes | Inventory SHA-256 |
|---|---:|---:|---|
| `inputs` | 2 | 776,640,636 | `8D02C484D8B223045302F056811CB77CC95C198DE7E52BF39E22721CB7DA1BD5` |
| `runs/original_hybrid` | 211 | 64,141,255 | `DCDFE5691D4799B30E08B9EBB30C370745089D934877AB1B622CD0F24E97F7F1` |
| `runs/original_pipeline_ocr` | 112 | 92,870,143 | `5978B97687721D7BFFCB53AD1618F03CFC3A6624489C07460529ED29F437F42B` |
| `runs/raster_hybrid` | 199 | 1,574,869,863 | `7354CCF5CFB82E85E410281A1E8C99D3FF172B2AEBF36662E2442BA47505A8C1` |
| `comparison` | 2 | 4,045,699 | `7E3521EA501DE38DE5CFD79A32DD730657358A78BCD30CBD6229D49BDC060638` |
| `evidence` | 6 | 65,135 | `5B8E2ED8DFF46AFAEC1538F2BC6F9D10E487B3AF14B4A68CCA51EF80A3AD53F5` |
| **fresh root total** | **532** | **2,512,632,731** | section digests above |

Key artifact hashes:

- `inputs/sample_pages.json`: 9,038 bytes,
  `4BE80A51F01B552536B1D51C3F43ABA90EAD31D87006F8FBB3FD48DEC2A4182E`;
- `comparison/comparison.json`: 4,045,127 bytes,
  `5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0`;
- `comparison/comparison.md`: 572 bytes,
  `51EAEB550BEBB70640DE9C219309C19DE8D91D38EEC49773E500138AA6AB5E54`;
- `evidence/prepare_raster_only.console.txt`: 349 bytes,
  `A008D862DEE222F53B4D91ACFD03C0E13BADAD31E1C0832F0C106E58EA51AF39`;
- `evidence/original_hybrid.console.txt`: 16,876 bytes,
  `EED1D3DF7FC8B55B632637E0BFA230A5217D8441AB41D20DF0DAD13227D67FB1`;
- `evidence/original_pipeline_ocr.console.txt`: 30,942 bytes,
  `05FF3993AE62F499BA525FC55444BE0A31BED235FB328B1F0FEA63B430C5B678`;
- `evidence/raster_hybrid.console.txt`: 16,656 bytes,
  `CAF9254B5E798B47BE4E2F66A2F616BF9C6DF953896E1023BDC747AF1840BF63`;
- `evidence/compare.console.txt`: 211 bytes,
  `0C24549CC1373CF59C069D7B51DA721F8633CCA6FB368E766ED59AFC3896A0C9`;
- `evidence/terra_focused_tests.console.txt`: 101 bytes,
  `85B31FD3681A9C5AA1A6D999B7ADFC721D4AD8C9A621614454E2F3DC0A0EC29C`.

## Blockers

No supplied-specification or file-scope blocker. No visual gate was attempted
by design and remains a separate downstream gate. The pipeline emitted a
transformers-version warning (`4.57.6` versus the runtime's requested range),
but native execution completed and no accepted machine contract failed.

An initial ancillary source-hash probe used an invalid positional
`Get-FileHash` invocation and produced a PowerShell parameter-binding error;
it changed no files and was immediately corrected with the exact
`-Algorithm SHA256 -LiteralPath` form, which confirmed the source identity
above. The frozen QA operations themselves all exited `0`.

## Next action

Reuse these immutable three-view outputs in the separately assigned visual
gate. Do not rerun any completed MinerU profile merely for this receipt.

