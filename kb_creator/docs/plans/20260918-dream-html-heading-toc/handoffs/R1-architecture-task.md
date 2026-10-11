# R1 architecture task — heading hierarchy and TOC

Goal: `20260918-dream-html-heading-toc`

Owner: architecture role (`gpt-5.6-sol`, high)

## Scope

Read-only root-cause and design review. Determine the earliest justified,
reusable correction layer for the Number 7 Dream Appendix C heading/order/TOC
defect without editing accepted masters or generated run09 artifacts.

## Evidence

- Run09 accepted-master inputs and Stage 40 output.
- Publication page evidence for pages 21–26 under run09 Stage 10 upstream.
- Reconstruction merge packets and visuals under
  `working/number-7-dream/reconstruction/20260917-cpu-replay-03`.
- `pipeline/publication_adapters.py`, `pipeline/translator.py`, related tests,
  contracts, and Number 7 Dream publication configs.
- Canonical plan/context in the parent directory.

## Required output

Write `R1-architecture-receipt.md` in this handoffs directory with:

1. proven root cause and full affected scope;
2. recommended correction layer(s), data/contract shape, and why;
3. legacy accepted-authority migration strategy;
4. failure gates and regression tests;
5. explicit forbidden shortcuts and residual risks.

## Forbidden

- No code/config/generated-output edits.
- No edits to plan.md, context.md, PROJECT_STATUS.md, accepted masters, or run09.
- No commit, push, acceptance, Stage 50, DOCX, or PDF.

