# Innsmouth v7 Rebuild Proof Context

Generated: 2026-07-30

## Objective

Use the current frozen Innsmouth v6 artifact set as the baseline and prove, or
falsify, that a fresh v7 rebuild can be produced through a script-backed
`kb_creator` wrapper.

## Accepted Constraints

- v6 files are frozen baseline and must not be overwritten.
- v7 outputs must use separate filenames and reports.
- `kb_creator` may call legacy `translator/translator.py` as a backend, but the
  reproducibility evidence belongs to `kb_creator`.
- If v7 differs in reader-facing content from v6, fix `kb_creator` by checking
  Translator behavior and rerun the rebuild/comparison loop.
- The result is a rebuild proof for KB preparation, not production approval.

## Completed State

The rebuild wrapper was implemented and run. It produced a fresh v7 rebuild
without overwriting the frozen v6 artifacts.

Evidence:

- `kb_creator/scripts/build_innsmouth_v7_rebuild.py`
- `kb_creator/reports/innsmouth_v7_rebuild/rebuild_report.json`
- `CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v7_rebuild.html`
- `CoC/Output/Scenarios/The_Innsmouth_Terror/Pdf/The_Innsmouth_Terror_Full_RU_v7_rebuild_two_column.pdf`

Result:

- `status=pass`
- `findings=0`
- reader-visible HTML text identical to v6 after normalizing only the service
  project-key marker
- image count: `34/34`
- table count: `156/156`
- statblock card count: `25/25`
- all required QA reports pass

Operational note: the PDF rebuild required escalated shell execution after a
normal sandboxed run hit an access-denied write to the temporary PDF render
HTML. The final result is still script-backed and recorded in the rebuild
report.

## Next Action

User visual review of the v7 HTML/PDF artifacts, then an explicit commit
request if this reproducibility proof should be recorded in Git.
