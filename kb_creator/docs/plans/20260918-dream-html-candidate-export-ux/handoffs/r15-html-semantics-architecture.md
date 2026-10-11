# R15 HTML semantic-projection architecture receipt

- Goal / step: `20260918-dream-html-candidate-export-ux` / `H7-html-semantics-architecture`.
- Role / model / effort: architecture and root-cause analysis; repository-policy model `gpt-5.6-sol`, high. Platform-selected model and effort are unverified.
- Orchestrator policy owner: `gpt-5.6-sol`, medium. Orchestration ownership was not transferred.
- Assignment state: completed architecture specification; implementation, QA, acceptance, staging, commit, and push were not performed.
- Scoped override: none.
- Scope: the two R14 Stage-40 defects only: quoted loose-list grouping and declared `statblock` / `blockquote` projection. This receipt is the only file changed.
- Result: `SPECIFIED / READY_FOR_BOUNDED_IMPLEMENTATION`. The canonical Markdown renderer owns list and line-flow correctness. The accepted reconstruction semantic sidecar owns statblock meaning. Stage 40 may project that meaning into its derived source only after an exact, fail-closed per-page container alignment; the canonical HTML config must not become semantic authority.

## Root cause and evidence

1. **Quoted loose list is split by the renderer.** In `translator/translator.py`, `markdown_to_review_html()` turns quoted blank lines into empty `quote_lines`, while `render_blockquote_lines()` skips each empty line and collects list items only while immediately consecutive. The page-14 source is one blockquote whose four `- ` items are separated by quoted blank lines, so each item starts a new `<ul>`. This is a parser/projection defect, not an authoring or Dream-specific defect.
2. **Trailing Markdown hard breaks are destroyed at the blockquote boundary.** The outer quote extraction uses `lines[i].strip().lstrip(">").strip()`. Its final `strip()` removes the two trailing spaces that `render_markdown_paragraph()` relies on to emit `<br>`. This affects any blockquote, independent of statblock typing.
3. **No declared semantic authority reaches the HTML renderer.** Run07's accepted reconstruction evidence declares seven page-18 top-level units with `kind=statblock` and `representation=blockquote`: `stanwick-statblock`, `elsie-statblock`, `regular-statblock`, `heavy-statblock`, `migo-man-statblock`, `migo-statblock`, and `hunting-horror-statblock`. Their full reviewed page decision supplies exact spans; `SEMANTIC_STRUCTURE.json` supplies matching span hashes and page-decision bindings. Stage 40 does not consume that authority.
4. **Existing statblock routes cannot classify these units.** `wrap_statblock_cards()` consumes configured heading IDs. `wrap_page_type_statblock_callouts()` consumes already typed statblock tables. The Dream page-18 units are blockquote containers, and the canonical HTML config declares neither scenario-specific heading IDs nor a semantic projection. The adapter's compact terminal-heading inference is inapplicable and must not be broadened into label, number, or vocabulary recognition.
5. **The pass gate has no expected semantic set.** Run07's `production_html_report.json` records `statblock_cards: 0`, `statblock_page_callouts: 0`, and `findings: 0`; therefore a successful render currently proves only syntactic output, not completeness against accepted semantic declarations. R14 independently found seven generic `review-callout` blockquotes and zero `.statblock-card` elements.

## Minimal scenario-neutral contract

### Authority decision

`SEMANTIC_STRUCTURE.json`, together with the page-decision files it hash-binds, is the authority for `kind`, `representation`, page, order, and semantic ID. The base HTML config remains presentation policy. It must not list Dream character names, headings, numeric-field patterns, or manually curated statblock IDs.

Stage 40 may write a sealed, derived `html_semantic_projection.json` and reference it from `derived_html_config.json`; that reference is transport, not new authority. The projection must bind the accepted semantic sidecar, the relevant page decisions, the accepted `MASTER_RU` bytes, and the derived Markdown bytes.

### Container alignment and projection

For every source page, perform these steps before invoking the renderer:

1. From the accepted page decision, enumerate in span order the complete set of **top-level container units** where `representation == "blockquote"` and `container_parent is null`. Validate every row against the corresponding compact sidecar row and page-decision hash.
2. From accepted `MASTER_RU`, split by page markers and enumerate the complete set of top-level Markdown blockquote containers in document order. A container is a maximal run of `>` lines; quoted blank lines (`>` or `> `) remain inside the same container, while an unquoted blank line ends it.
3. Require exact per-page count equality and pair the two complete sequences by ordinal. Do not filter the Markdown sequence down to suspected statblocks before alignment. This prevents an undeclared, inserted, omitted, or reordered quote from silently shifting authority.
4. Require unique semantic IDs, valid non-overlapping reviewed spans, a single page assignment, and no cross-page or nested-container pairing. Any mismatch is a hard Stage-40 error before renderer output.
5. For an aligned row with `kind == "statblock"`, insert the existing strict `<!-- callout-class: statblock-card -->` directive as the first quoted line in the **derived HTML source only**. Do not edit accepted `MASTER_RU`. Rows of any other kind keep their ordinary callout rendering.
6. Reject a pre-existing reserved `statblock-card` directive in accepted `MASTER_RU`; Stage 40 alone owns this derived projection. Record each projected semantic ID, page, ordinal, decision/span hash, and derived-container hash in the sealed projection evidence.

This is smaller and safer than adding a scenario-owned heading list to `html.json`, and it does not require lexical inference or a change to the accepted Markdown.

### Renderer behavior

- Preserve trailing whitespace while removing only the quote marker and at most one following separator space. Generic explicit Markdown hard breaks must therefore survive blockquote extraction.
- In `render_blockquote_lines()`, treat quoted blank lines between same-level items of the same list type as loose-list separators: one logical unordered sequence produces one `<ul>`; one logical ordered sequence produces one `<ol>`. Do not bridge across prose, headings, tables, images, directives, a list-type change, or the end of the blockquote.
- When the adapter-generated class is `statblock-card`, render ordinary physical lines within each paragraph group with `<br>` boundaries. Headings, tables, images, and lists retain their structural renderers. Ordinary `review-callout` paragraphs retain normal Markdown soft-line behavior except for explicit two-space hard breaks.
- Avoid double wrapping: a callout already carrying `statblock-card` must not also be wrapped by the legacy heading- or table-based paths.

### Fail-closed output invariants

- `expected_statblock_ids` is the exact set of aligned `kind=statblock`, `representation=blockquote` top-level units; for run07-derived evidence it has seven members.
- The final HTML must contain exactly one `.statblock-card` for each expected row, on the expected page and in the expected blockquote ordinal. Missing, duplicate, extra, or displaced cards fail the renderer/adapter even if HTML creation otherwise succeeds.
- The production report and adapter receipt must record expected count, rendered count, projected semantic IDs/pages/ordinals, projection SHA-256, and zero semantic findings. The adapter must independently reject a renderer report that says `pass` while the exact semantic set/count is not satisfied.
- If a page has no declared top-level blockquote containers but `MASTER_RU` has one, or vice versa, projection fails. There is no best-effort fallback to heading inference for that page.

## Compatibility and branching

- Existing packages without a semantic projection keep the current optional legacy heading/table statblock routes. The new strict gate applies when a semantic sidecar is supplied by the publication adapter.
- Existing `callout-class` rendering remains compatible. The adapter-generated reserved `statblock-card` directive takes precedence for its aligned container; legacy wrappers must skip it.
- Base scenario `html.json` remains unchanged except for genuine presentation choices. The derived runtime config may contain only a sealed projection identity/reference and rendering-mode selection.
- Ordinary paragraphs and ordinary blockquotes do not gain forced line breaks. The only general output changes are correct preservation of explicit two-space hard breaks and correct coalescing of loose-list items.
- `_compact_terminal_statblock_heading_ids()` may remain for v1 compatibility, but it is not semantic authority and must not run as a fallback for a page governed by a validated semantic projection.

## Exact implementation surfaces

1. `translator/translator.py`
   - preserve trailing spaces during blockquote-prefix removal;
   - coalesce blank-separated same-kind quoted list items;
   - pass typed callout context to `render_blockquote_lines()` and preserve physical statblock rows;
   - count final semantic cards after all wrappers and emit exact semantic projection findings/counts.
2. `kb_creator/pipeline/publication_adapters.py`
   - load and validate the accepted reconstruction sidecar/page decisions already packaged in the run authority graph;
   - align complete per-page top-level blockquote sequences against accepted `MASTER_RU`;
   - create and seal `html_semantic_projection.json`, inject only derived directives, bind it in `html_adapter_receipt.json`, and reject report/set drift;
   - keep `_augment_compact_statblock_policy()` as compatibility only, never as projection fallback on governed pages.
3. `kb_creator/tests/test_publication_html_adapter.py`
   - add adapter-level authority, alignment, directive-injection, report-binding, and failure regressions.
4. `translator/tests/test_recovery_support.py`
   - add renderer-level loose-list, hard-break, typed-line-flow, and double-wrap regressions.
5. `kb_creator/tests/test_publication_control_plane.py`
   - assert the new Stage-40 evidence/receipt binding and that implementation drift forces a fresh successor rather than mutating run07.

No schema expansion in `kb_creator/pipeline/semantic_structure.py` is required for the minimal fix: the full page decision already contains ordered spans, and the compact sidecar already binds their hashes. If implementation discovers that the packaged Stage-40 authority copy cannot resolve those existing files through declared run records, stop and add an explicit authority argument/binding; do not path-guess or copy semantic rows into the canonical HTML config.

## Required test matrix

| Layer | Positive case | Required negative cases |
|---|---|---|
| Blockquote renderer | Four `- ` rows separated by quoted blanks render one `<ul>` with four `<li>` | prose between items, list-type switch, unquoted block boundary, and nested/next heading do not merge |
| Ordered list symmetry | Quoted blank-separated numbered rows render one `<ol>` | unordered/ordered switch and intervening prose do not merge |
| Generic hard break | A quoted line ending in two spaces emits `<br>` | a normal soft line in an ordinary callout remains soft |
| Typed statblock | Declared derived callout emits one `.statblock-card`; all physical field/action rows remain visibly separated; nested quoted headings remain headings | same bytes without semantic declaration remain `review-callout`; pre-existing reserved directive is rejected |
| Semantic alignment | Complete per-page declared/container counts and order align; seven Dream page-18 rows project | missing, extra, reordered, cross-page, duplicate-ID, nested-as-top-level, sidecar hash drift, page-decision hash drift, and ambiguous container all fail before rendering |
| Output gate | Exact expected/rendered statblock set and count pass and are receipt-bound | renderer `pass` with zero, missing, duplicate, extra, or wrong-page card fails adapter |
| Compatibility | Existing heading-based compact statblock fixture still passes without semantic projection | validated projection never falls back to heading or vocabulary inference |
| End-to-end Dream | Fresh successor: page 14 has one four-item `<ul>`; page 18 has exactly seven `.statblock-card` elements with preserved row flow; 19/19 assets remain closed | run07 remains immutable and cannot be accepted/relabelled |

## Risks and fresh-run implications

- Page/order pairing is intentionally valid only after aligning the **complete** top-level blockquote sets per page. Aligning only the seven desired statblocks would be order-fragile and is rejected by this contract.
- Forced physical line breaks are scoped to typed statblocks; applying them to all blockquotes would alter prose callouts and is out of scope.
- The current report's `statblock_cards` variable counts legacy wrappers, not necessarily a class injected during initial Markdown rendering. The corrected count must be computed from the final HTML or from an exact rendered-ID ledger, otherwise a false zero/false pass can recur.
- Changes to `translator/translator.py` and `publication_adapters.py` change the fixed implementation identity. Run07 must remain immutable defect evidence. Build a fresh successor from the accepted authority graph, rebind prior accepted decisions only under the existing exact-equivalence rules, run Stage 40 again, and repeat bounded QA plus independent review. Do not record HTML acceptance or start Stage 50/DOCX/PDF from run07.

## Files checked / verification evidence

- Canonical goal `plan.md`, `context.md`, and R14 FAIL receipt.
- `translator/translator.py` blockquote parser, class directive, statblock wrappers, production report path, and existing renderer tests in `translator/tests/test_recovery_support.py`.
- `kb_creator/pipeline/publication_adapters.py`, including compact-heading inference and Stage-40 adapter; `kb_creator/tests/test_publication_html_adapter.py` and `test_publication_control_plane.py`.
- `kb_creator/pipeline/semantic_structure.py`, relevant semantic-structure tests, `scenario_master_ru.py`, and the MASTER_EN builder surface to confirm existing sidecar/span and translation-order contracts.
- Run07 accepted `MASTER_RU.md`, derived source/config, HTML, production report, accepted upstream `SEMANTIC_STRUCTURE.json`, and page-018 full reviewed decision. The full decision contains seven top-level statblock blockquotes at spans 5-8, 10-14, 16-18, 20-23, 25-30, 32-41, and 43-49; the compact sidecar contains matching IDs and span SHA-256 values.
- Verification type: read-only code and artifact inspection. No tests were run because this assignment specifies architecture, not implementation or QA.

## Blockers and next action

- Blockers: none for bounded implementation. Acceptance remains blocked by R14 until a fresh successor passes the matrix above.
- Next action: orchestrator assigns bounded implementation in the exact files above, preserves run07, builds a fresh successor, and requests bounded QA. Any inability to resolve the accepted semantic sidecar/page decisions through declared run authority is a stop condition, not permission for lexical heuristics.

## Accounting

- Elapsed time: approximately 35 minutes.
- Token use: unavailable to contributor.
- Timestamp: 2026-09-18 05:02 +03:00.
