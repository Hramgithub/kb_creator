# Innsmouth v7 Rebuild Proof Plan

Goal id: `20260730-innsmouth-v7-rebuild-proof`

Objective: rebuild Innsmouth artifacts through `kb_creator` as a separate v7
candidate and compare them with the frozen v6 baseline without overwriting v6.

## Steps

| Step | Owner | Effort | Status | Definition of Done | Evidence | Blocker | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Establish baseline contract | gpt-5.5 orchestrator | medium | completed | v6 freeze manifest is the only accepted input baseline | `kb_creator/inputs/innsmouth_v6_freeze_manifest.json` | none | Build wrapper |
| 2. Add rebuild wrapper | gpt-5.5 orchestrator | medium | completed | Script creates isolated v7 config and runs deterministic rebuild/check commands | `kb_creator/scripts/build_innsmouth_v7_rebuild.py` | none | Build completed |
| 3. Build v7 artifacts | gpt-5.5 orchestrator | medium | completed | v7 HTML/PDF are created without mutating v6 outputs | `CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v7_rebuild.html`; `CoC/Output/Scenarios/The_Innsmouth_Terror/Pdf/The_Innsmouth_Terror_Full_RU_v7_rebuild_two_column.pdf` | none | Compare completed |
| 4. Compare with baseline | gpt-5.5 orchestrator | medium | completed | Report records hashes, normalized differences, QA statuses, and warnings; content mismatch loops back to wrapper fixes | `kb_creator/reports/innsmouth_v7_rebuild/rebuild_report.json`: `status=pass`, `findings=0`, reader-visible text identical, images/tables/statblocks match | none | Status recorded |
| 5. Record handoff state | gpt-5.5 orchestrator | medium | completed | kb_creator status and context explain whether v7 proves reproducibility | `kb_creator/PROJECT_STATUS.md`; `context.md` | none | User visual review |

## Iteration Rule

If v7 differs from v6 by reader-facing content, image/table/statblock counts, or
required QA status, do not accept the rebuild. Inspect legacy Translator as the
behavior source, fix the `kb_creator` wrapper or contract, rerun the rebuild,
and compare again. Repeat until the report passes or a real blocker is
documented.

## Non-goals

- Do not overwrite v6 baseline artifacts.
- Do not claim production/release approval.
- Do not rebuild OCR, translation, or proofreading.
- Do not copy legacy Translator into `kb_creator`; call it as an external
  backend until Sourcefold/KB Creator has its own implementation.

## Result

Completed on 2026-07-30.

- Rebuild report: `kb_creator/reports/innsmouth_v7_rebuild/rebuild_report.json`.
- HTML artifact: `CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v7_rebuild.html`.
- PDF artifact: `CoC/Output/Scenarios/The_Innsmouth_Terror/Pdf/The_Innsmouth_Terror_Full_RU_v7_rebuild_two_column.pdf`.
- Reader-visible HTML text matches the v6 baseline after normalizing only the
  service project-key marker.
- HTML counts match the v6 baseline: images `34/34`, tables `156/156`,
  statblock cards `25/25`.
- QA statuses all pass: production HTML, statblock projection, positive
  content, CoC mechanics, art layout, production PDF, and PDF print QA.
- `findings=0`.
