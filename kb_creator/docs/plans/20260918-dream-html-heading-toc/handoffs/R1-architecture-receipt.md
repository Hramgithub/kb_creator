# R1 architecture receipt - heading hierarchy and TOC

- Goal id: `20260918-dream-html-heading-toc`
- Step id: `R1 / T2`
- Role: architecture
- Model: unavailable; repository-policy target `gpt-5.6-sol`
- Effort: high by assignment; platform value unavailable
- Orchestrator policy owner: main-chat `gpt-5.6-sol` at medium
- Assignment state: `platform-unverified`
- Scoped override: none
- Timestamp: `2026-09-18T10:38:55+03:00`
- Elapsed time: approximately 22 minutes
- Token use: unavailable

## Scope

Read-only root-cause and remediation design for the Appendix C heading/order/TOC
defect. No accepted master, generated output, code, config, canonical plan,
context, status, acceptance, or release file was changed. This receipt is the
only write.

## Verdict

`APPROVE_TWO_LAYER_REMEDIATION_SPECIFICATION`.

The immediate successor must correct a **derived Stage 40 Markdown projection
before Markdown parsing**, using an exact, reviewed, identity-bound legacy
heading-migration contract. The canonical prevention belongs earlier, in the
Stage 04/05/06 reconstruction semantic contract and validation. The renderer's
existing TOC depth filter is not the root cause and should not receive a title
deduplication heuristic.

A heuristic that promotes uppercase prose at Stage 40 is not approved. It
would violate `NRI_OCR_LAYOUT_RULES.md`: HTML may style typed semantics but may
not rediscover headings from untyped prose. The legacy bridge is acceptable
only when each operation is explicit, source-visual-bound, stale-sensitive,
and auditable.

## Proven root cause and full affected scope

### Earliest failing layer

The defect is present in the accepted reconstruction decisions, before
MASTER_EN, translation, and HTML:

1. Pages 21-26 are all classified as `semantic_role:
   pregenerated_characters` and visually use one repeated grammar: optional
   appendix root, one character title at the page top, statistics/skills, then
   `Background` and `What You Know About Stanwick` leaf sections.
2. The Stage 04 selected-block decisions and Stage 06 Markdown encode that
   grammar inconsistently:
   - page 21: Jocelyn title is a plain paragraph;
   - page 22: Milton title is `#` / level 1;
   - pages 23-25: Augustine, Ainsley, and Vincent titles are plain paragraphs
     placed at the **end** of their page Markdown, although their source bboxes
     are at y=59/60, above the portrait and statistics;
   - page 26: Camelia title is a plain paragraph at the page top;
   - all twelve repeated leaf headings are `##` / level 2.
3. `SEMANTIC_STRUCTURE.json` declares only one `line_group` unit on each of
   pages 21-26. It declares no heading units for the appendix root, six
   character titles, or twelve leaves. The current validator permits a
   semantic-unit set that is not structurally complete for the page role.
4. The OCR title signals are inconsistent, which explains but does not justify
   the result: the appendix is a recognized level-1 title; Milton alone is a
   recognized level-1 title; Jocelyn and Camelia have no title signal; the
   Augustine/Ainsley/Vincent source blocks are typed `header` but have no title
   evidence. All twelve leaves carry level-2 title evidence. No closed role
   grammar reconciles those signals with the reviewed visual.
5. MASTER_EN and MASTER_RU preserve that malformed order and hierarchy exactly.
   Stage 40 then parses what it was given. It does not invent the defect.

The visual evidence supports a single hierarchy. Page 21's appendix root bbox
is 71 pixels high; the six character-title bboxes are consistently 19-23
pixels high at y=59/60 (Jocelyn follows the root on page 21); leaf-title bboxes
are 15-17 pixels high lower in the page. The justified tree is therefore:

```text
H1 Appendix C
  H2 character 1
    H3 Background
    H3 What You Know About Stanwick
  H2 character 2
    H3 Background
    H3 What You Know About Stanwick
  ... six characters total
```

### Observable downstream scope

- Six character records are affected: five headings are missing and Milton is
  one level too high.
- Three of those six titles are also in the wrong reading position.
- Twelve leaf headings are one level too high.
- The current Appendix C TOC slice has 14 entries: one appendix, Milton, and
  twelve repeated leaves. The correct slice has seven entries: one appendix
  and six characters.
- The current HTML DOM confirms the same defect on pages 21-26. This is not a
  CSS-only or TOC-only discrepancy.

## Dependency trace

```text
source visual and OCR geometry
  -> Stage 04 selected blocks and reviewed page Markdown     [first defect]
  -> Stage 05/06 semantic validation                         [coverage gap]
  -> accepted reconstruction / MASTER_EN                     [preserves defect]
  -> accepted translation / MASTER_RU                        [preserves defect]
  -> Stage 40 derived_html_source.md                         [safe bridge point]
  -> markdown_to_review_html heading list
  -> filter_production_toc(max_heading_level=2)
  -> HTML body and generated TOC
```

`filter_production_toc` already defaults to `max_heading_level: 2`. Once the
body tree is H1/H2/H3, it naturally includes the appendix and character H2s and
omits the repeated H3 leaves. The TOC must be derived from corrected semantics;
it must not deduplicate visible titles.

## Remediation specification

### Layer A - canonical prevention in reconstruction

Upgrade the reusable reconstruction semantic contract so a reviewed page role
can declare an outline grammar and so the declared semantic units must cover it.
For `pregenerated_characters`, the profile should require:

- one record heading per page;
- an optional group/root heading only on the first page of a contiguous group;
- explicit leaf heading units subordinate to the record heading;
- `semantic_parent` relationships and consecutive levels `1 -> 2 -> 3`;
- record heading before portrait/stat/body content in reader order;
- every selected `purpose: structure` title block covered by exactly one
  heading unit;
- an exact visually reviewed heading override, bound to view/raw index, target
  reader text, level, reason, and reviewed visual identity, when OCR title
  evidence is absent or contradictory.

This should be a versioned, scenario-neutral contract/profile rather than a
hard-coded list of Number 7 Dream names. Stage 05 and Stage 06 must run the same
closed validation. Missing units, partial page coverage, invalid parent levels,
or a geometry/reader-order disagreement must fail closed.

This layer prevents recurrence in new reconstructions, but it cannot silently
rewrite the already accepted reconstruction or masters.

### Layer B - current legacy accepted-authority bridge at Stage 40

Add a generic, explicit `reviewed_legacy_migration` form to the Stage 40
semantic projection. It must run after exact MASTER_RU/ArtView rebinding and
before `markdown_to_review_html`, alongside the existing typed statblock
projection. A suitable config/contract shape is:

```json
{
  "schema": "kb_creator.semantic_heading_projection.v1",
  "mode": "reviewed_legacy_migration",
  "role_rules": [{
    "semantic_role": "pregenerated_characters",
    "page_scope": {"contiguous": true, "expected_count": 6},
    "root": {"current_level": 1, "target_level": 1, "expected_count": 1},
    "records": {
      "target_level": 2,
      "bindings": [
        {
          "source_page": 21,
          "source_visual_sha256": "...",
          "decision_sha256": "...",
          "master_en_line_sha256": "...",
          "master_ru_line_sha256": "...",
          "current_form": "paragraph",
          "current_position": "before_first_asset",
          "target_position": "after_root_or_page_marker"
        }
      ]
    },
    "leaves": {
      "current_level": 2,
      "target_level": 3,
      "expected_per_page": 2,
      "bindings": []
    },
    "expected_operations": {
      "record_promotions": 5,
      "record_demotions": 1,
      "record_moves": 3,
      "leaf_demotions": 12
    }
  }]
}
```

The row list is evidence, not implementation logic. It may contain audit labels
for human readability, but selectors must bind exact identities/hashes rather
than rely on names or capitalization. The generic code must not contain this
scenario's names, English/Russian leaf labels, or page numbers.

The projection output should be a sealed evidence artifact that records:

- identities of accepted MASTER_EN, MASTER_RU, reconstruction inventory,
  page decisions, and reviewed visuals;
- exact before/after page-subtree hashes;
- every promotion, demotion, and move with source page and heading role;
- final heading tree and expected TOC membership;
- operation counts and a projection hash.

The accepted masters remain byte-identical. Only the run-local
`derived_html_source.md` changes. If a later accepted reconstruction already
contains the correct tree, this legacy contract must fail as stale rather than
double-transform it.

### Renderer/TOC layer

No general title-deduplication or CSS repair is warranted. Keep the renderer's
existing maximum level policy at 2 for this profile and add verification that
the projected outline is reflected in both DOM and TOC. A renderer change is
needed only if integration shows it cannot preserve the corrected H1/H2/H3
tree; current code inspection and run09 behavior do not show such a defect.

## Failure gates and regression tests

### Projection gates

1. Exact accepted MASTER_EN, MASTER_RU, reconstruction inventory, decision,
   visual, config, and ArtView identities must match.
2. All and only the contiguous pages with the configured semantic role must be
   covered; partial coverage is fatal.
3. Every binding must match once in its declared page and current form/position.
4. Counts must be exactly `1 root / 6 records / 12 leaves`, with operations
   `5 promotions / 1 demotion / 3 moves / 12 leaf demotions`.
5. The result must be a valid tree: root H1, six H2 records in page order,
   exactly two H3 leaves below each record, no orphan leaf, no skipped level.
6. Accepted master bytes/hashes must be rechecked after projection.
7. Already-correct, ambiguous, duplicate, missing, translated-text-drifted, or
   wrong-role inputs must fail closed before renderer invocation.

### Tests

- Neutral synthetic multi-page record fixture with top and trailing record
  titles, mixed current paragraph/H1 forms, and repeated leaf headings.
- Negative tests for stale hashes, missing page, non-contiguous role pages,
  duplicate selector, missing leaf, multiple record candidates, wrong current
  level, invalid target parent, and already-correct input.
- Reconstruction tests that reject incomplete heading-unit coverage and accept
  exact visually reviewed heading overrides when OCR title evidence is absent.
- Adapter integration test proving the accepted master is unchanged and the
  derived Markdown has the exact H1/H2/H3 order.
- Renderer/TOC test proving seven Appendix C entries, six unique record hrefs,
  zero leaf entries, correct `toc-level-1/2`, and all destinations resolving.
- Real-candidate regression for page-14 callout, seven page-18 statblocks,
  19/19 images, zero missing references, and no Stage 50/DOCX/PDF output.

## Forbidden shortcuts

- Direct edits to MASTER_EN, MASTER_RU, run09, or generated HTML.
- `exclude_titles` lists for `Background` / `What You Know...`.
- Global TOC deduplication by visible text.
- `max_heading_level: 1` to hide the symptom.
- `heading_level_overrides` alone: it runs after Markdown parsing, cannot create
  the five missing headings, and cannot move the three trailing titles.
- Uppercase/name/age regex inference without exact reviewed bindings.
- CSS-only visual hierarchy, renderer-side prose promotion, or a Number 7
  Dream name list embedded in Python.
- Mutating an accepted authority and resealing it in place.

## Residual risks

- The promoted semantic sidecar records visual identities but does not carry
  the Stage 04 raster files inside the promotion package. The migration rows
  therefore need to bind those sealed identities and the explicit audit
  decision; Stage 40 must not claim it independently re-performed visual
  review.
- Accepted MASTER_EN/RU remain historically semantically malformed. The
  projection receipt must travel with the HTML package so later consumers do
  not treat the raw masters as already corrected. Downstream DOCX/PDF should
  consume the accepted corrected HTML lineage, not bypass the projection.
- A future reconstruction correction supersedes this bridge. Keeping both
  active would risk double transformation; stale-input rejection is mandatory.

## Files checked

- `kb_creator/docs/plans/20260918-dream-html-heading-toc/{plan.md,context.md}`
- `kb_creator/PROJECT_STATUS.md`
- `docs/governance/nri_goal_governance.md`
- `NRI_OCR_LAYOUT_RULES.md`
- `kb_creator/pipeline/{semantic_structure.py,publication_adapters.py}`
- `kb_creator/inputs/viral/production/pipeline/translator.py`
- `kb_creator/inputs/number-7-dream/publication/v1/configs/html.json`
- `kb_creator/tests/{test_semantic_structure.py,test_materialize_mineru_ai_merge.py,test_publication_html_adapter.py}`
- run09 accepted MASTER_EN, MASTER_RU, Stage 40 HTML, semantic sidecar, and
  page decisions 21-26
- replay-17 merge packets 21-26 and direct visual rasters for pages 21, 23,
  and 26; sealed visual/bbox evidence was checked for all pages 21-26

## Files changed

- `kb_creator/docs/plans/20260918-dream-html-heading-toc/handoffs/R1-architecture-receipt.md`

## Blockers

No blocker to implementing the specified two-layer fix. A heuristic-only
Stage 40 patch is blocked by the shared OCR semantic rules and should be
rejected.

## Next action

The orchestrator should implement the versioned reconstruction completeness
gate plus the exact reviewed legacy Stage 40 projection contract, add the
negative and integration tests above, author the six-page migration data from
the audited visual evidence, and build a fresh Stage 40 successor. Stop again
at explicit HTML acceptance; do not mutate run09 or proceed to Stage 50.
