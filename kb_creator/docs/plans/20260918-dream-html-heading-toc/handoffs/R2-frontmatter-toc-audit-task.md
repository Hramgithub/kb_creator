# R2 audit task — authors/frontmatter and source contents regression

Goal: `20260918-dream-html-heading-toc`

Owner: architecture/root-cause role (`gpt-5.6-sol`, high)

## Scope

Read-only trace of the previously established authors/frontmatter and
source-contents rules into the Number 7 Dream run09 Stage 40 path. Determine
exactly which rule/config/adapter step was lost or bypassed and why existing
tests did not prevent it.

## Evidence to inspect

- Project governance/status and prior Number 7 Dream plans/reviews.
- Git history for `translator/translator.py`, publication HTML configs, and
  `pipeline/publication_adapters.py`.
- Number 7 Dream accepted MASTER_RU, base/derived HTML configs, run09 HTML and
  producer evidence.
- Existing source-TOC/frontmatter tests and other scenario builders only as
  comparison evidence.

## Required output

Write `R2-frontmatter-toc-audit-receipt.md` with: intended recorded rule;
current active path; precise regression boundary; test-coverage gap; reusable
remediation contract; migration/compatibility notes; forbidden shortcuts.

## Forbidden

No code/config/output/plan/status edits. No commit, push, acceptance, Stage 50,
DOCX, or PDF. The only permitted write is the receipt.

