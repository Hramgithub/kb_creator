# R3 audit task — statblock presentation and title/row regression

Goal: `20260918-dream-html-heading-toc`

Owner: architecture/root-cause role (`gpt-5.6-sol`, high)

## Scope

Read-only trace of Appendix A statblock semantics and presentation through
reconstruction metadata, accepted masters, Stage 40 semantic projection,
renderer classes/CSS, and run09 DOM. Explain why the recent row-preservation
fix also produced quote/callout styling and why some names remain joined to the
first statistics row.

## Evidence to inspect

- Run09 pages/DOM/evidence for source page 18 and the exact accepted master
  excerpt.
- `pipeline/publication_adapters.py`, `translator/translator.py`, relevant
  configs, tests, and prior Number 7 Dream plans/reviews.
- Git history for the latest semantic statblock projection work.

## Required output

Write `R3-statblock-regression-audit-receipt.md` with: intended recorded rule;
root cause for visual quote styling; root cause for title/stat joining; full
affected scope; reusable semantic/presentation separation; verification gates;
forbidden shortcuts and residual risks.

## Forbidden

No code/config/output/plan/status edits. No commit, push, acceptance, Stage 50,
DOCX, or PDF. The only permitted write is the receipt.

