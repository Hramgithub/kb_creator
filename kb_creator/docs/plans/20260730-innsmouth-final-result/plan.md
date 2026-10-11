# Innsmouth KB Creator Final Result Plan

Goal id: `20260730-innsmouth-final-result`

Objective: produce a final reproducible Innsmouth `kb_creator` HTML/PDF result
from the accepted source chain: reader HTML, two-column PDF, manifests, and QA
evidence. The result must be reproducible by script, must not overwrite the
frozen v6 baseline, and must not modify any existing `Knowledge_Base*` files.

## Target Artifact Set

The final result is not just a proof report. It must include:

- accepted source evidence from the original PDF;
- accepted RU/Keeper input contract;
- reader HTML;
- two-column PDF;
- asset/art manifest;
- cross-link/index manifest for HTML/PDF anchors;
- QA reports proving structure, links, images, tables, statblocks, and print
  layout;
- final run report that records commands, hashes, timestamps, and pass/blocker
  status.

`Knowledge_Base*` directories are read-only for this goal. KB quality work is a
separate future goal; current acceptance is oriented by the frozen v6 HTML/PDF
baseline and the freshly generated comparison artifacts.

## Planned Outputs

| Artifact | Target path pattern | Required state |
| --- | --- | --- |
| Source proof report | `kb_creator/reports/innsmouth_full_dry_run/full_dry_run_report.json` | pass, retained as prerequisite evidence |
| Keeper Markdown evidence | `kb_creator/output/innsmouth_final/For_Keeper/KeeperBook.md` or manifest reference to accepted Keeper | accepted source text preserved, art markers/link anchors valid |
| HTML | `kb_creator/output/innsmouth_final/The_Innsmouth_Terror_Full_RU.html` or promoted scenario output path | reader-visible content complete, images/tables/statblocks present |
| PDF | `kb_creator/output/innsmouth_final/Pdf/The_Innsmouth_Terror_Full_RU_two_column.pdf` or promoted scenario output path | generated from current HTML, two-column body, protected frontmatter |
| Manifest | `kb_creator/reports/innsmouth_final/final_artifact_manifest.json` | hashes, sizes, source links, build commands |
| QA bundle | `kb_creator/reports/innsmouth_final/` | all required gates pass or explicit blocker |

Final target paths may be refined before implementation, but the manifest must
record the actual paths and hashes.

## Steps

| Step | Owner | Effort | Status | Definition of Done | Evidence | Blocker | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Freeze prerequisites | gpt-5.5 orchestrator | medium | completed | Existing full dry-run source and publishing proof is referenced and unchanged | `innsmouth_full_dry_run/full_dry_run_report.json` | none | done |
| 2. Define final HTML/PDF contract | gpt-5.5 orchestrator + Terra critic | medium/high | completed | Final artifact paths, manifest schema, no-KB-write invariant, and acceptance gates are explicit | `final_artifact_manifest.json` contract | none | done |
| 3. Build final HTML/PDF run script | gpt-5.5 orchestrator | medium | completed | Script produces separate final outputs and reports command/hash evidence | `kb_creator/scripts/build_innsmouth_final_result.py` | none | done |
| 4. Generate final HTML/PDF | gpt-5.5 orchestrator | medium | completed | HTML/PDF are freshly generated, then promoted to `kb_creator/output/innsmouth_final/` | `kb_creator/reports/innsmouth_final/runs/20260730T172713Z/final_run_report.json` | none | QA |
| 5. Final QA and comparison | Terra independent critic | high | completed | Frozen/source invariants pass; final HTML/PDF meet acceptance gates; KB write check is clean; visual evidence exists | `final_run_report.json`; `visual_pdf_review_report.md`; `handoffs/terra_release_review_20260730T203152.md` | none | done |
| 6. Record final state | gpt-5.5 orchestrator | medium | completed | `PROJECT_STATUS.md`, context, and final report summarize result, blockers, and next action | `context.md`; `PROJECT_STATUS.md`; `handoffs/terra_release_review_20260730T203152.md` | none | User visual review / commit decision |

## Acceptance Gates

The final result is accepted only if all of these are true:

- source PDF identity matches the recorded hash;
- raw and accepted-cleaned EN gates pass;
- no `Knowledge_Base*` file is modified by this goal;
- Keeper Markdown has no visible service placeholder text;
- HTML has no broken image references and includes all accepted images;
- HTML table/statblock counts meet or exceed the accepted v6 baseline unless a
  documented transformation explains the delta;
- PDF is generated after the current HTML, not reused from an older timestamp;
- PDF print QA passes;
- final artifact manifest records hashes and command evidence;
- Terra independent review is pass or final acceptance is marked pending.

## Explicit Non-goals

- Do not overwrite frozen v6 artifacts.
- Do not claim fresh LLM translation/proofreading unless that stage is actually
  rerun and independently reviewed.
- Do not commit generated final artifacts without explicit user request.
- Do not edit or regenerate KB files during this goal.

## Open Design Decisions

- Whether final outputs should later be promoted from
  `kb_creator/output/innsmouth_final/` into scenario output after visual review.
- Whether user visual review is required before final `production_approved`.

## Current Final Run

Run id: `20260730T172713Z`

- Report: `kb_creator/reports/innsmouth_final/runs/20260730T172713Z/final_run_report.json`
- Manifest: `kb_creator/reports/innsmouth_final/runs/20260730T172713Z/final_artifact_manifest.json`
- Visual evidence: `kb_creator/reports/innsmouth_final/runs/20260730T172713Z/visual_pdf_review_report.md`
- HTML: `kb_creator/output/innsmouth_final/runs/20260730T172713Z/The_Innsmouth_Terror_Full_RU.html`
- PDF: `kb_creator/output/innsmouth_final/runs/20260730T172713Z/Pdf/The_Innsmouth_Terror_Full_RU_two_column.pdf`
- Machine status: `pass`
- No-KB-write check: `pass`, files before/after `81/81`, findings `0`
- HTML comparison to frozen v6: reader-visible text identical, images `34/34`,
  tables `156/156`, statblocks `25/25`
- Boundary: accepted v6-derived RU/Keeper publishing chain only; no fresh
  translation/proofread claim.
- Note: previous runs `20260730T171157Z` and `20260730T172029Z` also passed
  machine checks, but were superseded by `20260730T172713Z` so visual evidence
  is generated and hashed by the runner itself.
- Terra independent release review: pass as reproducible HTML/PDF candidate,
  not production approval; receipt recorded in
  `handoffs/terra_release_review_20260730T203152.md`.
