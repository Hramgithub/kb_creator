# Innsmouth Full Dry-Run Proof Context

Generated: 2026-07-30

## Objective

Run the next proof level for Innsmouth:

`source PDF -> OCR/source reconstruction -> accepted text -> HTML/PDF`

and compare the result with frozen v6.

## Current Finding

The previous v7 rebuild proved only:

`frozen v6 config/content -> fresh HTML/PDF rebuild`

It did not rerun OCR, source reconstruction, translation, or proofreading.

`kb_creator` is currently documented as a downstream KB layer, with OCR,
translation, proofreading, and publishing out of scope. For this proof, it is
used as an experimental orchestration/evidence layer around reusable Translator
and project-local Innsmouth scripts.

## Reusable Source Evidence

Known source PDF:

`D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\1923_The Innsmouth Terror\The Innsmouth terror.pdf`

Expected source identity from runbook:

- bytes: `71396612`
- SHA-256: `CFD72DD3B8702C07750DCBB9F721A704793D6D474167B288922E6F7EBEEA561F`
- pages: `46`

Project-local source builder found:

`CoC/Working/Scenarios/The_Innsmouth_Terror/project/scripts/build_pymupdf_source_candidate.py`

It generates a fresh Full EN candidate from the source PDF using PyMuPDF
stream/block extraction and coordinate reading order. It is closer to the
accepted Innsmouth source method than raw OCR; column OCR remains repair
evidence rather than the accepted source.

## Current Risk

The accepted v6 source includes later recovery cleanup. A fresh PDF extraction
may match an earlier EN candidate but differ from the cleaned v6 accepted
source. If so, this is a real blocker for full reproducibility until that
cleanup is also script-backed and rerun through `kb_creator`.

## Stage 1 Result

The `kb_creator` wrapper was added and run:

`kb_creator/scripts/build_innsmouth_full_dry_run.py`

Report:

`kb_creator/reports/innsmouth_full_dry_run/full_dry_run_report.json`

Initial result:

- `status=blocked`
- findings: `1`
- source PDF exists and matches expected identity;
- page renders were generated from the source PDF;
- column OCR was rerun and produced the same candidate SHA as the historical
  accepted column OCR input:
  `ae99d986b49951d9f400884e99b82efd1e73a65853daf67e03e8d5489837311c`;
- reading-order reconstruction produced raw v6 EN byte-identical to accepted
  raw v6:
  `02af4ff1a155fe0360a6a52eb4168ccda678e9e01267eceac03140c38f4040fb`;
- deterministic cleanup produced the historical cleanup-report output
  `1e62a519b8d7d9eba3e5ba4034581b69cfa05113d014c53f32cdb6e2599adddb`;
- current accepted v6 cleaned EN is
  `d46dd93ba58731027aab4e35ad290f12f2b86ee9e347cf0e29c8097ca98bf178`,
  so the accepted-cleaned layer includes later edits not yet encoded in the
  full dry-run pipeline.

Fresh PyMuPDF comparison candidate:

`CoC/Working/Scenarios/The_Innsmouth_Terror/Formatted/The_Innsmouth_Terror_Source_Text_Full_EN_kb_full_dry_run_v1.md`

## Intermediate Blocker

`accepted_cleaned_source_has_unreproduced_post_cleanup_edits`

This is not a failed PDF/OCR extraction. It shows that PDF-to-source
reconstruction is reproducible through the accepted raw v6 source. The remaining
gap is the accepted-cleaned source layer: after deterministic cleanup, later
source fixes were applied or accepted outside the currently parameterized
`kb_creator` chain. Continuing to HTML/PDF would reuse stale accepted RU/Keeper
inputs and would not prove a full chain.

## Intermediate Next Action

Recover or encode the accepted-cleaned delta as a script-backed stage, then
rerun this goal. Only after fresh cleaned source matches accepted v6 may the
chain continue toward translation/proofreading and publishing.

## Final Result

The accepted-cleaned delta was recovered as a script-backed stage in
`kb_creator/scripts/build_innsmouth_full_dry_run.py`, then the full dry-run was
rerun.

Final report:

`kb_creator/reports/innsmouth_full_dry_run/full_dry_run_report.json`

Final status:

- `status=pass`
- findings: `0`
- source PDF identity passed:
  `cfd72dd3b8702c07750dcbb9f721a704793d6d474167b288922e6f7ebeea561f`
- raw EN candidate is byte-identical to accepted raw v6:
  `02af4ff1a155fe0360a6a52eb4168ccda678e9e01267eceac03140c38f4040fb`
- accepted-cleaned EN candidate is byte-identical to accepted cleaned v6:
  `d46dd93ba58731027aab4e35ad290f12f2b86ee9e347cf0e29c8097ca98bf178`

Publishing was run by script after the accepted source gates passed:

`kb_creator/reports/innsmouth_full_dry_run/publishing_rebuild/rebuild_report.json`

Publishing evidence:

- `status=pass`
- HTML:
  `CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v7_rebuild.html`
- PDF:
  `CoC/Output/Scenarios/The_Innsmouth_Terror/Pdf/The_Innsmouth_Terror_Full_RU_v7_rebuild_two_column.pdf`
- HTML reader-visible text matches frozen v6 after only service project-key
  normalization.
- Counts match frozen v6: images `34/34`, tables `156/156`, statblocks `25/25`.
- Production HTML, statblock projection, positive content, CoC mechanics, art
  layout, production PDF, and pdf-print QA all pass.

Important boundary: this does not prove a new LLM translation/proofread run.
It proves deterministic source reconstruction from the original PDF to accepted
EN, then script-backed HTML/PDF publishing from the already accepted v6
RU/Keeper/KB inputs. That is the intended freeze/reproducibility proof before
starting focused KB creation work.
