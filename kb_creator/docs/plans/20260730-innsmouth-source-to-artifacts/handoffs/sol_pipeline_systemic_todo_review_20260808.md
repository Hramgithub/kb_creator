# Sol Review - Innsmouth Pipeline TODO Systemic Analysis

Role: internal Sol mode.

Model/effort: unavailable / high.

Goal: analyze the user TODO as systemic pipeline issues, not individual page edits.

Timestamp: 2026-08-08.

## Summary

The TODO list points to one root problem: the pipeline still allows a
plausible-looking publication artifact to be produced before the source
reconstruction and semantic placement layers are fully accepted.

The failure chain is not one bug. It is a set of missing contracts between:

1. visible source PDF page structure;
2. accepted EN source reconstruction;
3. RU master preservation;
4. KeeperBook projection;
5. semantic art anchoring;
6. HTML/PDF rendering.

## Main Hypotheses

### H1 - Source reading order is not yet a hard prerequisite

The recurring page ranges with mixed columns suggest that the accepted EN source
can still inherit wrong block order from the OCR/extraction layer. Downstream
cleanup can make this look grammatical while preserving the wrong sequence.

Required correction:

- source reconstruction must have a page-level `reading_order_accepted=true`;
- two-column pages must have block order evidence, not only extracted text;
- pages without explicit repeated headings need a first-line column-order check.

### H2 - Cleanup rules are too local and pattern-specific

Findings such as split handout titles, broken names, table labels, and page
reference fragments are variants of one issue: OCR physical lines are leaking
into semantic Markdown.

Required correction:

- normalize source labels before translation;
- normalize page references and cross-references before Keeper projection;
- add negative QA for orphan labels, split labels, and broken proper names.

### H3 - Heading promotion is still allowed to leave body residue

Examples like `Прибытие / Прибытие: практическая справка`, duplicate heading
tails, and orphan section names show that the heading projection layer can
promote a heading while leaving the source line in body text.

Required correction:

- heading promotion must consume the source line;
- body residue checks must run after all projection passes, including art and
  statblock injection;
- duplicate heading-prefix checks must distinguish intentional subsection
  labels from accidental copied body residues.

### H4 - Art anchoring needs semantic identity, not only xref/page/order

The people-by-train and NPC portrait issues show that a page-local or ordering
heuristic can attach the right image to the wrong section. Original coordinates
are useful evidence, but final layout is independent of the source PDF, so the
anchor contract must be semantic.

Required correction:

- each publishable art item needs `subject`, `role`, `source_page`, `xref`,
  `source_anchor_text`, and `target_section_id`;
- if identity is uncertain, publication should block or mark the item for
  review rather than place it by fallback;
- page fallback should be allowed only for explicitly approved atmospheric or
  source-page visual items.

### H5 - Downstream pass status masks upstream blockers

Current downstream reports can be `pass` while `full_run_report.json` is still
blocked by source art anchoring. That means acceptance state is fragmented.

Required correction:

- final run status must aggregate upstream gates;
- a downstream `pass` must not imply release readiness when an upstream gate is
  blocked;
- the plan should record which artifact is preview-only and which is accepted.

## Recommended Work Order

1. Build an audit-only pass over the current run and the user TODO list.
2. Classify each finding by pipeline layer.
3. Repair source reconstruction / reading order before touching RU styling.
4. Repair semantic label normalization before translating or projecting.
5. Repair art semantic anchoring after the source spine is stable.
6. Rebuild KeeperBook, HTML, and PDF only after the source/projection gates pass.

## Risks

- Fixing final Markdown manually will hide pipeline defects and recreate the
  same failures on the next scenario.
- Anchoring art only by coordinates will fail when the final PDF layout changes.
- Comparing only rendered PDF is too late; the same visual symptom can come
  from source extraction, RU translation, or renderer projection.

## Handoff

Recommended next artifact:

`pipeline_todo_20260808.md` should become the active remediation checklist.
Each row should be linked to one QA finding or one accepted source exception.
