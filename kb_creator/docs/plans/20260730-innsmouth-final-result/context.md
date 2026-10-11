# Innsmouth KB Creator Final Result Context

Generated: 2026-07-30

## Objective

Move from a reproducibility proof to a final usable `kb_creator` HTML/PDF
result for Innsmouth.

Previous proof goal:

`source PDF -> OCR/source reconstruction -> accepted EN -> HTML/PDF rebuild`

passed and is recorded in:

`kb_creator/docs/plans/20260730-innsmouth-full-dry-run/`

This new goal extends the target:

`accepted source -> accepted Keeper/RU inputs -> HTML -> two-column PDF`

User correction, 2026-07-30:

Do not touch KB files in this goal. The current orientation is the PDF and HTML
artifacts. Existing `Knowledge_Base*` folders may be inspected for context only,
but must not be modified, regenerated, promoted, or used as the acceptance
target.

## Proven Prerequisites

The following are already proven and should be treated as prerequisites, not
re-litigated unless evidence changes:

- source PDF exists and matches SHA-256
  `cfd72dd3b8702c07750dcbb9f721a704793d6d474167b288922e6f7ebeea561f`;
- source PDF -> page renders -> column OCR -> reading-order raw EN reproduces
  accepted raw v6 byte-for-byte;
- accepted-cleaned EN reproduces accepted cleaned v6 byte-for-byte after the
  script-backed accepted-cleaned delta;
- HTML/PDF can be rebuilt from accepted v6 downstream inputs by script;
- publishing QA can pass for the rebuild.

Core evidence:

- `kb_creator/reports/innsmouth_full_dry_run/full_dry_run_report.json`
- `kb_creator/reports/innsmouth_full_dry_run/publishing_rebuild/rebuild_report.json`
- `kb_creator/scripts/build_innsmouth_full_dry_run.py`
- `kb_creator/scripts/build_innsmouth_v7_rebuild.py`

## Why This Goal Exists

The dry-run proof is necessary but insufficient. It proves that the current
accepted artifact chain is reproducible enough to protect against accidental
drift.

The user now needs an actual final HTML/PDF result:

- final reader HTML;
- final two-column PDF;
- manifests and QA proving the artifacts were generated from current accepted
  inputs;
- clear boundaries for what is accepted, pending, or excluded.

## Current Known Risk

The current successful dry-run does not prove fresh LLM translation or
proofreading. It reuses accepted v6 RU/Keeper/KB inputs after proving the EN
source reconstruction path.

For this goal, that is acceptable only if the final report says so plainly. If
fresh RU translation/proofreading becomes required, this goal must add explicit
LLM worker stages and independent review gates before claiming final accepted
RU.

Current no-KB-write boundary:

- `CoC/Output/Scenarios/The_Innsmouth_Terror/Knowledge_Base*` are read-only.
- `kb_creator/output/innsmouth_final/` may receive final HTML/PDF/manifest
  outputs.
- KB Creator may create reports about the HTML/PDF build, but no generated KB
  content in this goal.

## Role Model

- `gpt-5.5`: orchestrator, context owner, integration, user-facing synthesis.
- `gpt-5.6-terra`: engineering critic and independent final reviewer.
- `gpt-5.6-sol`: architecture/analysis of KB contract and extraction rules.
- `gpt-5.4`: bounded mechanical execution and QA after specs are accepted.

No agent may claim final acceptance without repository-backed evidence.

## Next Action

Before implementation:

1. inspect current Innsmouth HTML/PDF and publishing scripts;
2. define the final HTML/PDF contract and no-KB-write checklist;
3. decide output location strategy;
4. implement or adapt scripts so final HTML/PDF can be rebuilt by a single
   command or clearly ordered command set;
5. run final QA and record hashes in a manifest.

## 2026-07-30 Final Run Checkpoint

Implemented final HTML/PDF runner:

`kb_creator/scripts/build_innsmouth_final_result.py`

The first run `20260730T171048Z` correctly blocked because sandboxed PDF
rendering could not write the temporary Chrome render HTML, leaving a stale PDF.
This validated the freshness gate.

The second run `20260730T171157Z` was rerun with approved unsandboxed execution
for the final PDF rendering path and passed.

After Terra review, the runner was strengthened to record executable/tool
hashes and then to generate visual PDF evidence as part of the final run. The
current candidate run is `20260730T172713Z`; it supersedes `20260730T171157Z`
and `20260730T172029Z`.

Artifacts:

- HTML:
  `kb_creator/output/innsmouth_final/runs/20260730T172713Z/The_Innsmouth_Terror_Full_RU.html`
- PDF:
  `kb_creator/output/innsmouth_final/runs/20260730T172713Z/Pdf/The_Innsmouth_Terror_Full_RU_two_column.pdf`
- Final report:
  `kb_creator/reports/innsmouth_final/runs/20260730T172713Z/final_run_report.json`
- Manifest:
  `kb_creator/reports/innsmouth_final/runs/20260730T172713Z/final_artifact_manifest.json`
- Visual evidence:
  `kb_creator/reports/innsmouth_final/runs/20260730T172713Z/visual_pdf_review_report.md`

Evidence summary:

- freeze manifest validation: pass;
- full dry-run prerequisite: pass;
- rebuild report: pass;
- findings: 0;
- HTML reader-visible text equals frozen v6 after project-key normalization;
- image/table/statblock counts match frozen v6: `34/34`, `156/156`, `25/25`;
- PDF generated after current HTML;
- tool binary hashes recorded for Python, browser PDF engine, `pdftoppm`, and
  `pdfinfo`;
- visual PDF pages rendered: `32`, with spot review of pages 1, 2, 3, 17, 24,
  and 32;
- no-KB-write check: pass, `81` files before and after, no findings.

Acceptance boundary:

This is a reproducible HTML/PDF final candidate from accepted v6-derived
RU/Keeper inputs. It does not prove fresh LLM translation or proofreading and
does not modify KB content.

## 2026-07-30 Final Review Checkpoint

Terra independent release review completed for run `20260730T172713Z`.

Receipt:

`kb_creator/docs/plans/20260730-innsmouth-final-result/handoffs/terra_release_review_20260730T203152.md`

Disposition:

- `pass` as an HTML/PDF reproducibility candidate;
- not production approval;
- no Critical, High, or Medium findings;
- no blockers for candidate readiness;
- KB remains out of scope and no-KB-write evidence passed.

Current next action:

Ask the user to inspect the candidate HTML/PDF visually. Commit only after an
explicit user request.
