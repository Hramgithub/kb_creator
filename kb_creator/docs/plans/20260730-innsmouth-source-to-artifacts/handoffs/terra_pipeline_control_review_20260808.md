# Terra Review - Innsmouth Pipeline Controls

Role: internal Terra mode.

Model/effort: unavailable / high.

Goal: turn the user TODO and Sol hypotheses into enforceable controls.

Timestamp: 2026-08-08.

## Summary

The pipeline needs an audit-first remediation stage. The immediate priority is
not to rebuild another PDF, but to make the TODO list executable: each class of
failure should be detectable before publication.

## Proposed Controls

### C1 - User TODO audit report

Create or extend a script that emits:

`QA/user_todo_structure_audit.json`

The report should contain one row per TODO ID and per detected instance:

- `todo_id`;
- `status`;
- `layer`;
- `page`;
- `section`;
- `evidence`;
- `suggested_fix`;
- `blocking`.

### C2 - Source reading-order gate

For every source page with two-column layout:

- preserve block IDs with source page and column;
- store first visible line per column;
- compare accepted EN source order against expected column order;
- fail if right-column content appears before left-column content without an
  explicit source exception.

Pages already called out by the user must be seed fixtures:

- 020/021 `Brewster Residence`;
- 021/022 `Наткнуться на съёмочную площадку`;
- 022/023;
- `Эпический финал`;
- `На съёмочной площадке`;
- `Bazzledon's Office`.

### C3 - Semantic label normalization gate

Add checks for:

- `Таблица\s*\n+\d+`;
- `Раздаточный материал\s*\n+\d`;
- `стр\.\s*\n+\d+`;
- known page reference fragments not converted to links;
- orphan source headings such as isolated `Расследование`;
- old printed page numbers attached to headings or body text.

### C4 - Heading/body residue gate

After KeeperBook generation, scan for:

- heading text repeated at start of first body paragraph;
- heading prefix duplicates;
- body lines that match the source TOC label spine;
- intentional subsection headings that need a configured exception.

This gate must run after reader-art insertion and statblock projection, because
those passes can alter local structure.

### C5 - List/body boundary gate

Detect paragraphs where a list continuation is glued to body prose, especially:

- `Кабинет продюсера`;
- `На съёмочной площадке`;
- locations where source bullets begin with clue/procedure text and are followed
  by narrative paragraphs.

The gate should not decide style. It should only flag missing list boundaries,
unexpected bullet loss, and impossible single paragraphs that contain multiple
source block starts.

### C6 - Table and handout title gate

Canonicalize:

- `Table N: title` -> `Таблица N: title`;
- `Handout N: title` -> `Раздаточный материал N: title`;
- split handout labels with parenthetical page references into one logical
  title/reference line.

QA should fail on split labels in EN source, RU master, and KeeperBook.

### C7 - Semantic art anchor gate

The publishable art manifest must include:

- source evidence: `source_page`, `xref`, optional `bbox`;
- semantic evidence: `role`, `subject`, `source_anchor_text`;
- target evidence: `target_section_id`;
- decision: `approved`, `rejected`, `deferred`, or `source_exception`.

Rules:

- coordinates can support extraction and evidence;
- final placement must use semantic `target_section_id`;
- page fallback must be blocked unless explicitly approved for that role.

### C8 - Aggregated final status

`full_run_report.json` should fail if any upstream gate fails. A rebuilt
HTML/PDF with local `pass` reports is preview-only while the aggregate report is
blocked.

## Implementation Plan

1. Add `pipeline_todo_20260808.md` as the active backlog.
2. Add audit-only scripts/reports before changing content.
3. Seed fixtures from the user examples and the known `xref-01172` art blocker.
4. Classify every finding by layer.
5. Fix the earliest failing layer first.
6. Rebuild KeeperBook/HTML/PDF only after the relevant upstream gate passes.
7. Commit only after the user explicitly asks or after a scoped implementation
   request includes commit.

## Handoff

Current recommendation:

- do not close the current Innsmouth source-to-artifacts goal;
- add the TODO package to the plan as the next active remediation stage;
- keep `source_art_anchor_layer_failed` visible until the semantic art anchor
  gate passes.
