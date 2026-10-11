# R3 statblock presentation and title/row regression audit receipt

## Handoff metadata

- Goal id: `20260918-dream-html-heading-toc`
- Step id: `R3-statblock-regression-audit`
- Role: architecture / root-cause analysis
- Requested policy model and effort: `gpt-5.6-sol`, high
- Actual platform model and effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol`, medium
- Assignment state: `platform-unverified`
- Scoped override: none
- Scope: read-only trace of Appendix A source page 18 from visual/reconstruction evidence through accepted masters, Stage 40 projection, renderer DOM/CSS, tests, prior plans/reviews, and Git state
- Result: `SPEC_READY / RUN09 REJECTED FOR THIS DEFECT CLASS`
- Files changed: this receipt only
- Timestamp: `2026-09-18T10:44:42+03:00`
- Elapsed time: approximately 22 minutes
- Token use: unavailable

## Executive result

Two independent contract failures are present.

1. **The quote/callout appearance is created at Stage 40.** Reconstruction correctly types all seven page-18 containers as `kind=statblock`, but uses Markdown `representation=blockquote` as a portable transport. Stage 40 then injects `<!-- callout-class: statblock-card -->`; the renderer always starts a Markdown blockquote with class `review-callout` and merely appends `statblock-card`. The resulting DOM is `<blockquote class="review-callout statblock-card">`, so the global `blockquote.review-callout` beige background, brown left border, padding, and margins necessarily apply. The semantic type was therefore coupled back to quote presentation at the renderer boundary.

2. **Four title/stat joins originate before MASTER_EN.** The page-18 source visual shows seven distinct colored character-name headings. MinerU exposes `STANWICK WEBB`, `THE MIGO MAN`, and `MIGO` as separate text/title blocks, but folds `ELSIE WEBB`, `ENLIGHTENED (REGULAR)`, `ENLIGHTENED (HEAVY)`, and `HUNTING HORROR` into the first table/stat block (`raw_index` 255, 258, 261, and 274). Those four blocks have `v2_title=false` and `markdown_heading=false`. The reviewed semantic contract allows a `statblock` without a title child and has no reviewed intra-source-block split binding, so the flattened lines were accepted into reconstruction, MASTER_EN, and MASTER_RU. Stage 40 reproduces them faithfully; CSS is not the cause.

The prior fixes were incomplete rather than lost at runtime. The structural-fidelity work recorded the semantic distinction between a statblock and a quotation, but the later HTML remediation deliberately reused the callout renderer. Its tests assert `class="review-callout statblock-card"` as success. The row-preservation QA checked seven card classes and per-card `<br>` counts, but did not require a neutral container or one title element per card. Earlier MASTER_RU QA explicitly allowed proper names to remain in statistic lines. Thus the regression suite canonized the partial fix and had no negative gate for either user-visible defect.

## Intended recorded rule

The durable rule was already present but was not enforced across the final boundary:

- `NRI_OCR_LAYOUT_RULES.md` requires cards/stat blocks to remain structurally separate from prose; a source-visible quote, callout, handout, list, table, or stat block must receive semantic reconstruction plus a typed sidecar; HTML may style accepted structure but must not rediscover or conflate it.
- `a5-structural-contract-architecture.md` states that a typed sidecar preserves the semantic difference between a quotation, handout, and statblock even when portable Markdown uses blockquote syntax. In other words, `representation=blockquote` is serialization, not permission to render quote chrome.
- The same rules require source heading hierarchy to be preserved and forbid heuristic splitting/joining of title words. A visually separate statblock title must be represented explicitly before production output.

The correct invariant is therefore:

> Semantic kind controls the HTML container and presentation role; Markdown representation controls only accepted-source serialization. A statblock serialized as Markdown blockquote is not a quotation and must not acquire quote semantics or callout styling. Every visually reviewed statblock title declared by the source contract must remain a separate title node, never part of the first statistics row.

## Evidence and dependency trace

### 1. Source visual and extraction evidence

- Bound Stage-04 visual: `reconstruction/20260918-cpu-replay-17/.../original_pipeline_txt/pages/page-018.png`, also sealed by the page decision as SHA-256 `BC4F554A39FBDD5A19C5917D99DEEDC97AE249905DD814EA40CDC1C6E169E3FE`.
- It shows seven distinct visual titles: Stanwick Webb, Elsie Webb, Enlightened (Regular), Enlightened (Heavy), The Migo Man, Migo, and Hunting Horror.
- Stage-04 packet `page-018.json` exposes only three as separate title-capable text blocks: 251, 263, and 268.
- Four title-bearing visual regions are flattened into table text: 255, 258, 261, and 274. Each is `type=table`, `v2_table_text=true`, `v2_title=false`, and `markdown_heading=false`.

This is the earliest information-model gap for title separation: the visual evidence exists, but the normalized block interface has no reviewed sub-block title segment for those four tables.

### 2. Reconstruction and accepted-master evidence

The promoted page decision declares exactly seven top-level `statblock / blockquote` units, but only three nested `heading / atx_heading` children:

- headings present: `stanwick-statblock-title`, `migo-man-statblock-title`, `migo-statblock-title`;
- headings absent: Elsie, Regular, Heavy, Hunting Horror.

`semantic_structure.py` validates the closed `kind/representation` pair and optional containment, but the statblock shape has no `title_required`, `title_role`, or source-slice binding. A parent statblock without a heading child is therefore valid. Reusing raw block 255/258/261/274 as a child heading cannot work under the current contract because each raw block's complete text includes both title and statistics, while the child heading span would contain only the title.

Accepted MASTER_RU preserves the result exactly:

- line 527: separate `### СТЭНВИК УЭББ`;
- line 532: `ЭЛСИ УЭББ` joined to `СИЛ ...`;
- line 538: `ПРОСВЕТЛЁННЫЙ (ОБЫЧНЫЙ)` joined to `СИЛ ...`;
- line 542: `ПРОСВЕТЛЁННЫЙ (СИЛОВИК)` joined to `СИЛ ...`;
- line 547: separate `### ЧЕЛОВЕК-МИ-ГО`;
- line 554: separate `### МИ-ГО`;
- line 565: `УЖАС-ОХОТНИК` joined to `СИЛ ...`.

Therefore the four title defects are already present in accepted MASTER_EN and accepted MASTER_RU. A Stage-40 CSS or DOM-only patch cannot restore them without inventing a new semantic decision.

### 3. Stage-40 projection and quote styling

`kb_creator/pipeline/publication_adapters.py::_semantic_html_projection()`:

- aligns the complete per-page top-level blockquote sequence against sealed reconstruction semantics;
- recognizes `unit.kind == "statblock"`;
- injects `> <!-- callout-class: statblock-card -->` into the derived HTML source;
- gates only class count, page, and blockquote ordinal.

`translator/translator.py::markdown_to_review_html()`:

- initializes every Markdown blockquote as `callout_class = "review-callout"`;
- appends the directive class, yielding `review-callout statblock-card`;
- emits a `<blockquote>` element.

The production stylesheet applies beige callout chrome to every `blockquote.review-callout`. Run09 DOM confirms all seven Appendix A cards use that exact class. Thus the rendering is behaving exactly as the current code and tests require, but the requirement is wrong.

The row-preservation change itself works: typed statblocks preserve physical rows through `<br>`, and run09 has per-card counts `2,4,2,3,4,8,6`. Its trigger, however, is the appended callout class, which coupled row behavior to quote presentation.

### 4. Why prior QA did not stop this

- R15 specified the adapter-generated `callout-class: statblock-card` directive and called the result a typed callout. It did not require removal of `review-callout` or a neutral HTML element.
- `translator/tests/test_recovery_support.py` positively asserts `class="review-callout statblock-card"`.
- `kb_creator/tests/test_publication_html_adapter.py` uses the same DOM in its passing semantic-projection fixture and gates only card count/ordinal.
- R17 and R18 record seven `review-callout statblock-card` nodes and `<br>` counts as pass evidence; neither checks computed presentation or title-node completeness.
- Earlier MASTER_RU QA records that proper names remain in some lines as allowed by that check's scope.

These are missing or inverted acceptance criteria, not a nondeterministic renderer failure.

### 5. Git evidence

The current semantic Stage-40 projection and row-preservation work exists only in the dirty working tree relative to HEAD `8a81ada0`; no later commit appears in Git history for the relevant files. Run09 was built from those active changes, so lack of a commit did not cause the visible defects, but it is a reproducibility and recovery risk until a corrected implementation is reviewed and explicitly committed.

## Full affected scope

| Defect | Current Number 7 Dream scope | Generic scope |
|---|---|---|
| Quote/callout presentation | All 7 Appendix A statblocks on source page 18 | Every future `kind=statblock, representation=blockquote` projected through the current Stage-40 directive path |
| Missing title node / title joined to first row | 4 of 7: Elsie Webb, Enlightened (Regular), Enlightened (Heavy), Hunting Horror / `УЖАС-ОХОТНИК` | Any visually titled statblock whose extractor folds the title into a table/text block and whose reviewed contract does not declare a bound sub-block title segment |
| Row preservation | Currently retained for all 7 and must not regress | Typed statblocks only; ordinary quotations/callouts must keep normal Markdown soft-line behavior |

The current semantic sidecar contains no other statblock units outside page 18. Ordinary quotations, callouts, and handouts are not candidates for neutral statblock rendering and must retain their own presentation contracts.

## Reusable remediation contract

### A. Separate semantic kind, source serialization, and presentation

1. Treat these as three different fields/concepts:
   - semantic kind: `statblock`, `quote`, `callout`, `handout`;
   - accepted Markdown representation: `blockquote`, `table`, etc.;
   - publication presentation role: neutral stat card, quotation, advisory callout, handout facsimile.
2. Stage 40 must map sealed `kind=statblock` to a neutral semantic container such as `<section class="statblock-card" data-semantic-kind="statblock">` or `<div ...>`. It must not emit a `<blockquote>` and must not add `review-callout`.
3. Replace the overloaded `callout-class` transport with a typed semantic projection record/directive. The projection remains derived and identity-bound; it must carry semantic ID, page, ordinal, accepted span identity, and intended renderer role.
4. Renderer defaults must fail closed when a supplied semantic kind has no explicit mapping. Falling back from statblock to generic blockquote/callout is forbidden.
5. Legacy heading/table statblock routes may remain versioned compatibility paths, but they must not override or double-wrap a governed semantic projection.

### B. Add a reviewed title contract at reconstruction

1. Version the structural profile so a reviewed statblock may declare an exact title role and whether it is required by the bound visual review.
2. Support reviewed intra-source-block segmentation for extractor blocks that contain both title and body. A generic binding should identify an exact source block plus exact source text slice/range and hash, not infer from capitalization, names, stat labels, or vocabulary.
3. For a titled statblock, require exactly one title child before body rows. Validate:
   - the title slice is visually reviewed and lies within a selected source block;
   - the reader title occurs exactly once as the declared heading/title node;
   - the first body/stat row excludes the title text;
   - title precedes all body rows and remains inside the same statblock parent;
   - no text is lost or duplicated across title/body partitions.
4. Stage 05 and Stage 06 must both enforce the same partition/title invariant and seal it into `SEMANTIC_STRUCTURE.json`.
5. Because the four joins already exist in accepted reconstruction and both accepted masters, produce a fresh upstream reconstruction successor and corresponding MASTER_EN/MASTER_RU successors. Do not claim closure by transforming accepted MASTER_RU only at Stage 40. Existing accepted packages remain immutable historical evidence.

### C. Keep row flow independent

1. Preserve the current typed-statblock physical-row renderer, but trigger it from the semantic presentation role, not a CSS/callout class token.
2. Preserve headings, tables, images, and lists as structural children; use `<br>` only for reviewed physical stat rows within the neutral card.
3. Ordinary blockquotes/callouts retain explicit Markdown hard breaks only and do not gain forced row behavior.

## Verification gates and acceptance criteria

### Reconstruction / masters

- Bound source page 18 has exactly 7 statblock parents and exactly 7 reviewed title nodes.
- The four formerly flattened raw blocks 255, 258, 261, and 274 have exact reviewed title/body partitions.
- MASTER_EN and MASTER_RU each contain seven separate title lines/nodes; none of the seven first stat rows begins with or contains the title prefix.
- Full lexical/mechanics closure proves no text loss, duplication, row reorder, or translated-value drift.
- Removal of any title child, title slice, partition hash, or body boundary makes both Stage 05 and Stage 06 fail.

### Stage 40 / renderer

- Page 18 has exactly 7 neutral `.statblock-card` containers in the sealed semantic ID/page/ordinal order.
- It has exactly 7 title elements, one per card, with the accepted Russian titles.
- It has zero `blockquote.statblock-card`, zero `.review-callout.statblock-card`, and zero statblock containers matching the quote/callout CSS selector.
- Browser-computed checks show no beige callout background, no callout left border, and no callout padding on statblocks.
- Physical row boundaries remain present for all seven cards; page-14 four-item callout list and ordinary quotes/callouts remain unchanged.
- Missing/extra/reordered cards, missing/duplicate titles, unknown presentation mapping, or renderer/report disagreement fails before candidate publication.

### Regressions

- Neutral synthetic statblock serialized as Markdown blockquote renders as a neutral card, not a quote.
- The same Markdown bytes typed as ordinary quotation render as `review-callout`; semantic kind, not syntax, decides presentation.
- A source block containing `TITLE + first stat row` fails without reviewed partition metadata and passes only with an exact title/body split.
- Tests explicitly reject the old successful fixture `<blockquote class="review-callout statblock-card">`.
- A fresh Number 7 Dream successor is visually inspected at page 18 and stops before HTML acceptance/Stage 50.

## Forbidden shortcuts

- Do not hide the defect with CSS overrides while retaining `<blockquote>` or `review-callout` on statblocks.
- Do not regex-split titles by uppercase text, names, characteristic labels, digits, language, or scenario page number.
- Do not hard-code the seven Dream names, IDs, or page 18 in reusable renderer code/config.
- Do not hand-edit run09, accepted MASTER_EN/MASTER_RU, or generated HTML.
- Do not create titles for the four merged blocks only in Stage 40 without a reviewed upstream semantic binding.
- Do not apply forced `<br>` behavior to all blockquotes.
- Do not weaken semantic count/order/hash gates or treat a visual-only pass as structural acceptance.
- Do not relabel run09 as corrected, accepted, or release-ready.

## Residual risks and assumptions

- Changing statblocks from `<blockquote>` to a neutral container affects downstream selectors in DOCX/PDF conversion and print CSS; those paths need focused compatibility tests before any Stage 50 work, but they remain outside this audit.
- A versioned semantic-profile change is preferable to silently tightening legacy accepted packages. Historical packages should retain explicit legacy dispatch.
- A new reconstruction/master successor may change unit identities and translation packet bindings even if Russian lexical content is reused exactly; strict rebinding and new acceptance evidence are required.
- Exact source-slice offsets must be defined on stable normalized bytes and hash-bound; character offsets over differently normalized Unicode/newlines would be fragile.
- Current uncommitted implementation work remains susceptible to loss or accidental mixing until the corrected goal passes independent review and the user explicitly authorizes a scoped commit.

## Files checked and verification/evidence

Checked, read-only:

- goal plan/context and R3 task packet under `docs/plans/20260918-dream-html-heading-toc/`;
- `NRI_OCR_LAYOUT_RULES.md`, `kb_creator/README.md`, `kb_creator/PROJECT_STATUS.md`, and NRI goal governance;
- reconstruction and publication contracts for Number 7 Dream;
- run09 accepted MASTER_EN/MASTER_RU, derived HTML source/config, semantic projection, producer report, DOM, and page-18 reviewed decision;
- replay-17 page-18 Stage-04 packet and bound source visual;
- `kb_creator/pipeline/semantic_structure.py` and `publication_adapters.py`;
- `translator/translator.py` and focused renderer/adapter tests;
- prior structural-fidelity and HTML semantic-projection plans/receipts;
- Git status, log, and relevant working-tree diffs.

Verification was static/read-only. No code, config, output, canonical plan/status, acceptance, commit, push, Stage 50, DOCX, or PDF action was performed.

## Blockers and next action

- Audit blocker: none.
- Implementation constraint: the current goal's statement that accepted MASTER_EN/MASTER_RU remain the sole immutable authorities is incompatible with fully correcting the four title joins, because those defects are already present in both masters and the current sidecar lacks title-split authority.
- Next action for the orchestrator: integrate this finding into the canonical plan, explicitly authorize/version an upstream semantic-title successor before the Stage-40 rebuild, then assign bounded implementation against sections A-C and the verification matrix above.
