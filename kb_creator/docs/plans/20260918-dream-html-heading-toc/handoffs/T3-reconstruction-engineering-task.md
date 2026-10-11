# T3 reconstruction semantic completeness engineering task

- Goal: `20260918-dream-html-heading-toc`
- Owner role: engineering, repository-policy `gpt-5.6-terra`, medium
- Ownership: reconstruction semantic contract/validator, its authoring support,
  promotion compatibility needed by that version, and focused tests only.
- Forbidden: scenario decision edits, generated outputs, accepted authorities,
  publication renderer/adapter, canonical plan/status, acceptance, Git commit.

## Inputs

Read the active plan/context and R1/R3 receipts. The current v1 validator checks
only declared units. It accepts `pregenerated_characters` pages with no heading
units and `character_statistics` statblocks without title children. Four Dream
titles are folded into one extractor block with their first stat row.

## Required implementation

1. Add an explicit opt-in, backward-compatible next semantic profile/schema;
   do not silently tighten historical v1 decisions.
2. Support an exact reviewed source fragment/partition binding for a semantic
   unit when one selected source block contains both title and body. Bind stable
   normalized bytes/text and SHA-256; reject missing, stale, ambiguous,
   overlapping, lossy, duplicated, or out-of-range partitions. Never infer a
   title from capitalization, names, labels, language, or page number.
3. For the opted-in `character_statistics` role, require every top-level
   statblock to contain exactly one title heading before body rows and prove
   full title/body conservation.
4. For the opted-in `pregenerated_characters` role, require the reviewed
   outline grammar `optional root H1 on the first contiguous page -> exactly
   one record H2 per page -> declared leaf H3 children`, valid semantic parents,
   reader order, and complete heading coverage. Keep the contract generic.
5. Stage 05 and Stage 06 must use the same validator and sidecar profile.
   Update promotion/replay compatibility only as required for this new explicit
   version while retaining legacy dispatch.
6. Add positive neutral fixtures and negatives for missing/duplicate titles,
   stale partitions, text loss/duplication, invalid parents/levels/order,
   noncontiguous pages, and v1 compatibility.

## Verification and receipt

Run the smallest focused suites covering all changed code, then the directly
dependent reconstruction tests. Write a compact receipt at
`T3-reconstruction-engineering-receipt.md` with changed files, exact commands,
counts, limitations, and any migration requirements. You are not alone in the
worktree: preserve unrelated and concurrent edits; never revert them.

