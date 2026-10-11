# T4 renderer semantic presentation and frontmatter engineering task

- Goal: `20260918-dream-html-heading-toc`
- Owner role: engineering, repository-policy `gpt-5.6-terra`, medium
- Ownership: `translator/translator.py` and focused translator renderer tests.
- Forbidden: KB Creator adapter/config authoring, scenario config/decisions,
  generated output, accepted authority, canonical plan/status, Git commit.

## Inputs

Read active plan/context and R2/R3 receipts. Existing Stage 40 injects a
`callout-class: statblock-card` directive. Markdown rendering always begins
with `review-callout`, producing a quote-styled blockquote. Frontmatter support
exists but uses split defaults; non-custom landing placement ignores credits,
and prose credits are not covered by the current page-map route.

## Required implementation

1. Add an explicit typed semantic directive/transport for statblocks. A governed
   statblock serialized from Markdown blockquote syntax must render as a neutral
   `<section>` or `<div class="statblock-card" data-semantic-kind="statblock">`,
   with no `<blockquote>` and no `review-callout`. Preserve physical stat rows
   and nested headings/tables/lists. Ordinary quotations/callouts stay unchanged.
   Unknown typed semantic kinds must fail closed. Keep any legacy callout route
   explicitly compatible but separate.
2. Make all source-TOC phases consume one resolved TOC/frontmatter policy rather
   than different missing-field defaults. Preserve existing valid modes.
3. Extend credits transformation for an explicitly declared prose credits page
   without requiring a table, and support `credits before TOC` when the landing
   is the source page rather than a custom landing asset.
4. Add positive and negative tests: neutral typed statblock vs ordinary quote;
   rejection/absence of old combined class; row preservation; source order
   `cover -> credits -> source_toc -> body`; prose credits; no duplicate source
   TOC; current legacy modes remain valid.

## Verification and receipt

Run focused translator suites and report exact counts. Write
`T4-renderer-engineering-receipt.md`. You are not alone in the worktree:
preserve unrelated and concurrent edits; never revert them.

